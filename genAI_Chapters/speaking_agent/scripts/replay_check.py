"""Phase 0: kya DB ka llm_contents wapas valid Gemini history ban sakta hai?

Run (project root se, app.main ki tarah):
    python -m scripts.replay_check
    python -m scripts.replay_check --conversation-id conv_xxx --turns 5
    python -m scripts.replay_check --no-signatures   # optional negative control


    Function	        :                Responsibility
has_function_call()	    :       Tool call present hai ya nahi
is_replayable()	        :       History structurally valid hai ya nahi
load_sample_turns()	    :       MongoDB se turns fetch
rebuild_python_mode()   :       Dict → Gemini Content
print_first_difference():       First mismatch debug
report_signatures()	    :       Thought signatures inspect
check_roundtrip()	    :       Conversion equality validate
strip_signatures()	    :       Signatures remove
replay_against_api()    :       Actual Gemini API test
parse_args()	        :       CLI arguments parse
main()	                :       Complete execution orchestrate


"""
import argparse
import json
import sys
import traceback

from google import genai
from google.genai import types

from core.config import settings
from database.mongodb_client import turns_collection
from llms.history import contents_from_docs
from prompts.system import SYSTEM_PROMPT
from tools.schema_builder import build_gemini_tools

REPLAYABLE_STATUSES = ["success", "partial_failure", "awaiting_confirmation"]
PROBE_QUESTION = (
    "Do not call any tools. Do not Hallucinate.In one short sentence, "
    "what was the first thing I asked in this conversation?"
)


def has_function_call(turn_doc: dict) -> bool:
        # Purpose: Check karna ki particular turn mein Gemini ne koi tool/function call kiya tha ya nahi.
        #expected gemini injection data structure:  
            #         {
            #   "role": "model",
            #   "parts": [
            #     {
            #       "function_call": {
            #         "name": "get_weather",
            #         "args": {
            #           "city": "Vizag"
            #         }
            #       }
            #     }
            #   ]
            # }
        return any(
        part.get("function_call")
        for content in turn_doc.get("llm_contents", [])
        for part in content.get("parts", [])
    )


def is_replayable(turn_doc: dict) -> bool:
    """Valid turn: user text se shuru, model message pe khatam."""
    # First message ka role user hona chahiye. First message ke kisi part mein text key ppakka honi chahiye. Last message bhi model ka hona chahiye.
    contents = turn_doc.get("llm_contents") or []
    if not contents:
        return False
    first, last = contents[0], contents[-1]
    starts_with_user_text = first.get("role") == "user" and any(
        "text" in part for part in first.get("parts", []) # Check if the first message contains text
    )
    return starts_with_user_text and last.get("role") == "model" # last message ka role "model" hona chahiye, taaki Gemini ko pata chale ki user ne kya bola aur model ne kya reply diya.


def load_sample_turns(conversation_id: str | None, limit: int):
    # Purpose: MongoDB se testing ke liye conversation turns fetch karna.
    query: dict = {"status": {"$in": REPLAYABLE_STATUSES}}

    if conversation_id is None:
        # sabse [LATEST] naya tool-call wala turn dhundo, usi pe khatam hone wale turns lo
        anchor = turns_collection.find_one(
            {
                # MongoDB ka $in operator specified statuses mein se matching documents select karta.
                "status": {"$in": ["success", "partial_failure"]}, 
                "tool_calls.0": {"$exists": True},
                "llm_contents.0": {"$exists": True},
            },
            sort=[("created_at", -1)],
        )
        if anchor is None: # agar koi tool-call wala turn nahi mila toh user ko inform karna aur exit karna
            raise SystemExit(
                "Tool-call wala turn nahi mila. Pehle app chala ke weather query karo."
            )
        conversation_id = anchor["conversation_id"]
        query["turn_index"] = {"$lte": anchor["turn_index"]}

    query["conversation_id"] = conversation_id
    docs = list(turns_collection.find(query).sort("turn_index", -1).limit(limit))
    docs.reverse()

    usable = [d for d in docs if is_replayable(d)]
    skipped = [d["turn_index"] for d in docs if not is_replayable(d)] # Valid turns usable mein aur invalid turns skipped mein.
    return conversation_id, usable, skipped


def rebuild_python_mode(docs: list[dict]) -> list[types.Content]: # Is function ka purpose MongoDB JSON/dictionaries ko Gemini SDK ke Python objects mein convert karna hai.
    return [types.Content.model_validate(doc) for doc in docs]


def print_first_difference(expected: list[dict], actual: list[dict]) -> None: # meant for debugging, to show where the round-trip conversion failed
    for index, (stored, rebuilt) in enumerate(zip(expected, actual)):
        if stored != rebuilt:
            print(f"  first difference at content #{index}")
            print("  stored :", json.dumps(stored)[:300])
            print("  rebuilt:", json.dumps(rebuilt)[:300])
            return
    print(f"  length mismatch: stored={len(expected)} rebuilt={len(actual)}")


def report_signatures(stored: list[dict], rebuilt: list[types.Content]) -> None:
    # Purpose: Gemini ke thought_signature ko verify karna.
    # Gemini ke function calling workflow mein thought signatures important ho sakte hain, especially multi-step tool calling ke waqt.
    stored_sigs = [ # stored mein thought_signature parts ko extract karna, taaki rebuilt ke saath compare kiya ja sake
        part["thought_signature"]
        for content in stored
        for part in content.get("parts", [])
        if "thought_signature" in part
    ]
    rebuilt_sigs = [
        part.thought_signature
        for content in rebuilt
        for part in (content.parts or [])
        if part.thought_signature is not None
    ]
    print(f"  thought_signature parts: stored={len(stored_sigs)} rebuilt={len(rebuilt_sigs)}")
    if stored_sigs and rebuilt_sigs:
        first = rebuilt_sigs[0]
        print(
            f"  first signature: stored str len={len(stored_sigs[0])}, "
            f"rebuilt type={type(first).__name__} len={len(first)}"
        )
        # sahi decode hua toh bytes ki length string se ~25% chhoti hoti hai
        if isinstance(first, bytes) and len(first) < len(stored_sigs[0]):
            print("  -> base64 decode hua (sahi)")
        else:
            print("  -> decode NAHI hua (galat)")


def check_roundtrip(name: str, rebuild, stored: list[dict]):
    # Purpose: MongoDB se fetched llm_contents ko Gemini SDK ke Python objects mein convert karke wapas JSON mein convert karna, aur check karna ki round-trip conversion sahi hai ya nahi.
    print(f"\n--- {name} ---")
    try:
        rebuilt = rebuild(stored)
    except Exception as exc:
        print(f"  FAIL rebuild: {type(exc).__name__}: {exc}")
        return None

    dumped = [c.model_dump(mode="json", exclude_none=True) for c in rebuilt]
    equal = dumped == stored
    print(f"  {'PASS' if equal else 'FAIL'} round trip equal")
    if not equal:
        print_first_difference(stored, dumped)
    report_signatures(stored, rebuilt)
    return rebuilt if equal else None


def strip_signatures(contents: list[types.Content]) -> list[types.Content]:
    # Purpose: Thought signatures ko remove karna, taaki Gemini API ke against test kar sake bina signatures ke.
    stripped = []
    for content in contents:
        copy = content.model_copy(deep=True)
        for part in copy.parts or []:
            part.thought_signature = None
        stripped.append(copy)
    return stripped 


def replay_against_api(history: list[types.Content]) -> None:
    # Purpose: Rebuilt history ko Gemini API ke against test karna, taaki verify ho ki API ne accept kiya ya reject kiya.
    client = genai.Client(api_key=settings.gemini_keys[0]) 
    probe = types.Content(role="user", parts=[types.Part(text=PROBE_QUESTION)])

    response = client.models.generate_content(
        model=settings.model_name,
        contents=[*history, probe], # history ke baad probe question add karna, taaki model ko pata chale ki yeh ek test hai aur koi tool call nahi karna hai. and *history Python unpacking hai.
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=build_gemini_tools(),
            temperature=0,
        ),
    )

    print(f"  model reply: {response.text!r}")
    if response.function_calls:
        print("  note: model ne tool call kiya (probe mein mana tha)")

    usage = response.usage_metadata
    print("  usage_metadata (Phase 1 ka pehla look):")
    for field in (
        "prompt_token_count",
        "candidates_token_count",
        "thoughts_token_count",
        "cached_content_token_count",
        "total_token_count",
    ):
        print(f"    {field}: {getattr(usage, field, None)}")


def parse_args() -> argparse.Namespace:
    # Purpose: Command-line arguments ko parse karna, taaki user specific conversation ID ya turns specify kar sake.
    parser = argparse.ArgumentParser(description="Phase 0 replay check")
    parser.add_argument("--conversation-id", default=None)
    parser.add_argument("--turns", type=int, default=5)
    parser.add_argument(
        "--no-signatures",
        action="store_true",
        help="API call se pehle thought_signature hata do (sirf jaankari ke liye)",
    )
    return parser.parse_args()


def main() -> int:
    # Purpose: Complete execution orchestrate karna, including fetching turns, rebuilding history, and replaying against Gemini API.
    args = parse_args()
    conversation_id, turns, skipped = load_sample_turns(
        args.conversation_id, args.turns # taaki user specified conversation ID aur turns limit ke hisaab se MongoDB se turns fetch ho sake
    )
    if not turns: # agar koi valid turns nahi mile toh user ko inform karna aur exit karna
        print("Koi replayable turn nahi mila (llm_contents missing ya adhoora).")
        return 1

    stored = [content for turn in turns for content in turn["llm_contents"]] # MongoDB se fetched turns ke llm_contents ko flatten karke ek list mein store karna, taaki round-trip validation aur API replay ke liye use kiya ja sake.
    tool_turns = [t["turn_index"] for t in turns if has_function_call(t)] # tool call wale turns ko identify karna, taaki user ko inform kiya ja sake ki kitne turns mein tool call hua tha

    print(f"conversation : {conversation_id}")
    print(f"turns used   : {[t['turn_index'] for t in turns]}")
    print(f"turns skipped: {skipped} (adhoora/purane format)")
    print(f"tool turns   : {tool_turns}")
    print(f"contents     : {len(stored)}")
    if not tool_turns:
        print("WARNING: sample mein function_call wala turn nahi, test kamzor hai.")

    check_roundtrip("model_validate (python mode)", rebuild_python_mode, stored)
    rebuilt = check_roundtrip(
        "model_validate_json (contents_from_docs)", contents_from_docs, stored
    )
    if rebuilt is None:
        print("\nVERDICT: FAIL. contents_from_docs ka round trip match nahi hua.")
        return 1

    label = "no signatures" if args.no_signatures else "with signatures"
    print(f"\n--- real API call ({label}) ---")
    history = strip_signatures(rebuilt) if args.no_signatures else rebuilt
    try:
        replay_against_api(history)
    except Exception:
        traceback.print_exc()
        print("\nVERDICT: FAIL. API ne rebuilt history reject ki.")
        return 1

    print("\nVERDICT: PASS. DB se history rebuild + API accept.")
    return 0


if __name__ == "__main__":
    sys.exit(main())