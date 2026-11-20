"""Phase 1 smoke: ek real LLM call, LLMCallRecord print karo.

Run: python -m scripts.llm_smoke
"""
from llms import chat
from llms import history as his

def main() -> None:
    contents: list = []
    his.append_user_query(contents, "Say hi in one short sentence.")

    for i in range(7):
        response, record = chat.generate_content(history=contents, iteration=1)
        usage = record.usage
        print(
            f"call {i}: key={record.key_index} prompt={usage.prompt_tokens} "
            f"cached={usage.cached_tokens} latency={record.latency_ms}ms" 
            # implicit caching erratic hai,
        )

if __name__ == "__main__":
    main()