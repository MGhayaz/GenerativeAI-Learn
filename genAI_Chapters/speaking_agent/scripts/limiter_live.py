"""Phase 2: bada tool output cap hota hai ya nahi (LLM ke bina).

Run: python -m scripts.limiter_live
"""
from tools.command import execute_command
from workflow.tool_handler import build_tool_response_part


def main() -> None:
    result = execute_command(
        "1..400 | ForEach-Object { 'line number ' + $_ + ' of the test output' }"
    )
    raw = result.result or ""
    print(f"success={result.success} raw chars={len(raw)}")

    part = build_tool_response_part("execute_command", result) 
    capped = part.function_response.response["result"]
    print(f"capped chars={len(capped)}")
    print("head:", capped[:60].replace("\n", " | "))
    print("tail:", capped[-60:].replace("\n", " | "))


if __name__ == "__main__":
    main()