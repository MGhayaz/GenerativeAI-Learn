"""Phase 1 extra: latency kis cheez se badhti hai?

Run: python -m scripts.latency_probe
"""
import statistics

from llms import chat
from llms import history as his
from llms.history import contents_from_docs
from scripts.replay_check import load_sample_turns, strip_signatures

RUNS = 3
SIMPLE = "Say hi in one short sentence." # Purpose: Pata karna ki normal Gemini API kitni fast hai.
LONGER = "Tell me a short joke in two sentences." # Purpose: Check karna ki response generate karne mein zyada time lag raha hai ya nahi.
FOLLOWUP = "In one short sentence, what did I ask first in this conversation?" # Purpose: Check karna ki database se reconstructed history ki wajah se latency badh rahi hai ya nahi. and Check karna ki signatures ki wajah se latency badh rahi hai ya nahi.


def with_user(history: list, text: str) -> list:
    contents = list(history)
    his.append_user_query(contents, text)
    return contents


def probe(label: str, history: list) -> None:
    latencies = []
    usage = None
    for _ in range(RUNS):
        _, record = chat.generate_content(history=history, iteration=1)
        latencies.append(record.latency_ms)
        usage = record.usage
    print(
        f"{label:<30} prompt={usage.prompt_tokens:<5} out={usage.output_tokens:<4} "
        f"latencies={latencies} median={int(statistics.median(latencies))}ms"
    )


def main() -> None:
    _, turns, _ = load_sample_turns(None, 3)
    stored = [c for t in turns for c in t["llm_contents"]]
    rebuilt = contents_from_docs(stored)

    probe(f"A: tiny prompt: {SIMPLE}", with_user([], SIMPLE))
    probe(f"B: tiny, longer answer: {LONGER}", with_user([], LONGER))
    probe(f"C: DB history + signatures: {FOLLOWUP}", with_user(rebuilt, FOLLOWUP))
    probe(f"D: DB history, no signatures: {FOLLOWUP}", with_user(strip_signatures(rebuilt), FOLLOWUP))


if __name__ == "__main__":
    main()