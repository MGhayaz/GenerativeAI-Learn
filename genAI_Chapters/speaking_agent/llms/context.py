import logging
from dataclasses import dataclass, field
from google.genai import types
from llms.usage import estimate_content_tokens, estimate_tokens
from models.schemas import ContextInfo

logger = logging.getLogger(__name__)

# Sirf ye statuses history mein jaate hain. failed turn adhoora hota hai
# (function_call bina response ke ho sakta hai), agli call ko 400 dega.
RETAINED_STATUSES = frozenset({"success", "partial_failure", "awaiting_confirmation"})


# notes : Trim ek-ek turn ke bajaye ek saath hota hai: HIGH cross hone pe LOW tak. Beech ke turns mein history ka shuruaati hissa same rehta hai (cache ka chance), aur trim kabhi-kabhi hota hai. 
# File Purpose : Ye file conversation state aur context building ke liye hai. Ye decide karta hai ki kaunse turns ko LLM ko dikhana hai, aur kaunse turns ko compact ya trim karna hai, taki LLM ke input budget mein fit ho sake.
# File end to end workflow : ConversationState mein turns store hote hain, aur build_context function ko call karke LLM ke liye context banate hain. Ye function decide karta hai ki kaunse turns ko include karna hai, kaunse turns ko compact karna hai, aur kaunse turns ko drop karna hai, taki LLM ke input budget mein fit ho sake.



@dataclass(frozen=True)
class TurnUnit:
    """Ek completed turn: user text se final model text tak, balanced."""
    turn_index: int
    contents: list[types.Content]
    footprint_tokens: int | None
    status: str


@dataclass
class ConversationState:
    conversation_id: str
    turns: list[TurnUnit] = field(default_factory=list)
    window_start: int = 0  # 3b mein trimming isi se hogi, abhi hamesha 0

    def commit_turn(
        self,
        turn_index: int,
        contents: list[types.Content],
        footprint_tokens: int | None,
        status: str,
    ) -> bool:
        """Turn end pe call karo. Retained status ho toh state mein jodta hai."""
        if status not in RETAINED_STATUSES:
            return False
        self.turns.append(
            TurnUnit(
                turn_index=turn_index,
                contents=list(contents),  # copy: caller ki list baad mein badle toh asar nahi
                footprint_tokens=footprint_tokens,
                status=status,
            )
        )
        return True

@dataclass(frozen=True)
class ContextParams:
    input_budget_tokens: int      # ek call ka soft prompt limit
    fixed_overhead_tokens: int    # S: system prompt + tool schemas
    tool_reserve_tokens: int      # R: tool loop ke liye jagah
    low_ratio: float = 0.6
    keep_full_turns: int = 2      # itne recent turns ke outputs compact nahi hote
    min_recent_turns: int = 2     # itne turns kabhi drop nahi hote
    old_output_max_chars: int = 300
    chars_per_token: float = 3.5

@dataclass(frozen=True)
class BuiltContext:
    contents: list[types.Content]
    turns_included: int
    window_start: int = 0
    info: ContextInfo = field(default_factory=ContextInfo)

@dataclass(frozen=True)
class _TurnView:
    contents: list[types.Content]
    footprint: int       # effective footprint (compaction ke baad)
    chars_saved: int

# shrink,compact_content : purane tool outputs ko compact karna, aur window trim karna.

def _shrink(text: str, max_chars: int) -> str | None:
    """text ko chhota stub banao. Stub original se chhota na ho toh None (chhedo mat)."""
    if len(text) <= max_chars:
        return None
    stub = text[:max_chars] + f"... [trimmed {len(text) - max_chars} chars]"
    return stub if len(stub) < len(text) else None


def compact_content(
    content: types.Content,
    max_chars: int,
) -> tuple[types.Content, int]:
    """Purane turn ke function_response ke bade 'result'/'error' strings chhote karo.

    Copy pe kaam hota hai, original kabhi mutate nahi. Kuch compact nahi hua toh
    wahi original object wapas aata hai. Part structure, function_call aur text
    kabhi nahi chhedte, taaki call/response ki pairing na tootey.
    Returns (content, chars_saved).
    """
    parts = content.parts or []
    if not any(part.function_response for part in parts):
        return content, 0

    compacted = content.model_copy(deep=True)
    chars_saved = 0
    for part in compacted.parts or []:
        resp = part.function_response
        if resp is None or not resp.response:
            continue
        for key in ("result", "error"):
            value = resp.response.get(key)
            if not isinstance(value, str):
                continue
            stub = _shrink(value, max_chars)
            if stub is None:
                continue
            chars_saved += len(value) - len(stub)
            resp.response[key] = stub

    if chars_saved == 0:
        return content, 0
    return compacted, chars_saved    

def _view_turn(turn: TurnUnit, compact: bool, params: ContextParams) -> _TurnView:
    """F7: turn ka LLM ko dikhne wala view aur uska effective footprint."""
    base = turn.footprint_tokens
    if base is None:  # purane docs ya usage missing: estimate
        base = max(
            1,
            sum(estimate_content_tokens(c, params.chars_per_token) for c in turn.contents),
        )

    if not compact:
        return _TurnView(list(turn.contents), base, 0)

    contents: list[types.Content] = []
    chars_saved = 0
    for content in turn.contents:
        compacted, saved = compact_content(content, params.old_output_max_chars)
        contents.append(compacted)
        chars_saved += saved

    saved_tokens = int(chars_saved / params.chars_per_token)
    return _TurnView(contents, max(1, base - saved_tokens), chars_saved)

def build_context(
    state: ConversationState,
    user_text: str = "",
    params: ContextParams | None = None,
) -> BuiltContext:
    """Turn ke start pe EK baar call karo. State ko mutate nahi karta.

    params None: koi trimming ya compaction nahi (3a behavior).
    Warna: purane turns compact (F7), HIGH cross ho toh LOW tak sabse purane turns drop (F6).
    Naya window_start BuiltContext mein aata hai, caller state mein save kare.
    """
    turns = state.turns
    start = state.window_start

    if params is None:
        window = turns[start:]
        return BuiltContext(
            contents=[c for t in window for c in t.contents],
            turns_included=len(window),
            window_start=start,
            info=ContextInfo(
                window_start_turn_index=window[0].turn_index if window else None,
                turns_in_window=len(window),
                turns_dropped_total=start,
            ),
        )

    # F7: sirf last keep_full_turns poore, baaki compact
    full_from = len(turns) - params.keep_full_turns
    views = [
        _view_turn(turn, compact=index < full_from, params=params)
        for index, turn in enumerate(turns[start:], start=start)
    ]

    # F5: budget
    user_est = estimate_tokens(user_text, params.chars_per_token)
    high = max(
        0,
        params.input_budget_tokens
        - params.fixed_overhead_tokens
        - user_est
        - params.tool_reserve_tokens,
    )
    low = int(high * params.low_ratio)

    # F6: watermark trimming
    total = sum(view.footprint for view in views)
    new_start = start
    if total > high:
        limit = max(start, len(turns) - params.min_recent_turns)
        while total > low and new_start < limit:
            total -= views[new_start - start].footprint
            new_start += 1
        if total > high:
            logger.warning(
                "Recent turns alone (%d tokens) exceed history budget (%d)", total, high
            )

    kept = views[new_start - start:]
    contents = [content for view in kept for content in view.contents]

    if contents:
        first = contents[0]
        if first.role != "user" or not first.parts or not first.parts[0].text:
            raise ValueError("Built context must start with a user text content.")

    info = ContextInfo(
        window_start_turn_index=turns[new_start].turn_index if new_start < len(turns) else None,
        turns_in_window=len(kept),
        turns_dropped_total=new_start,
        turns_compacted=sum(1 for view in kept if view.chars_saved > 0),
        chars_saved_by_compaction=sum(view.chars_saved for view in kept),
        trimmed_this_turn=new_start > start,
        fixed_overhead_tokens=params.fixed_overhead_tokens,
        history_high=high,
        history_low=low,
        predicted_prompt_tokens=params.fixed_overhead_tokens + total + user_est,
    )
    return BuiltContext(
        contents=contents,
        turns_included=len(kept),
        window_start=new_start,
        info=info,
    )