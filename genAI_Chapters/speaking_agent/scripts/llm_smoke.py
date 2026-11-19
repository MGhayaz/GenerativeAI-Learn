"""Phase 1 smoke: ek real LLM call, LLMCallRecord print karo.

Run: python -m scripts.llm_smoke
"""
from llms import chat
from llms import history as his


def main() -> None:
    user_text = "Say hi in one short sentence."
    contents: list = []
    his.append_user_query(contents, user_text)

    response, record = chat.generate_content(history=contents, iteration=1)

    print("reply:", response.text)
    print(record.model_dump_json(indent=2))


if __name__ == "__main__":
    main()