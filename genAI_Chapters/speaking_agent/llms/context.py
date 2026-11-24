


from dataclasses import dataclass, field
from google.genai import types

# Sirf ye statuses history mein jaate hain. failed turn adhoora hota hai
# (function_call bina response ke ho sakta hai), agli call ko 400 dega.
RETAINED_STATUSES = frozenset({"success", "partial_failure", "awaiting_confirmation"})


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
class BuiltContext:
    contents: list[types.Content]
    turns_included: int


def build_context(state: ConversationState) -> BuiltContext:
    """3a: koi trimming nahi, sab turns flatten. 3b mein budget aur compaction aayega."""
    turns = state.turns[state.window_start:]
    contents = [content for turn in turns for content in turn.contents]
    return BuiltContext(contents=contents, turns_included=len(turns))