from types import SimpleNamespace

"""new keyword "assert" ke bareme
    The assert keyword in Python is a debugging statement used to test if a condition is True. IF the condition evaluates to TRUE, the PROGRAM CONTINUES EXECUTING NORMALLY. IF it evaluates to FALSE, Python immediately halts execution and RAISES AN ASSERTIONERROR, optionally with a specified error message. This is useful for catching bugs and validating assumptions during development.
"""
# overview : ye file llms/usage.py ke functions ku test karra. ye file me estimate_tokens, estimate_content_tokens, extract_usage, compute_footprint, sum_usage functions ku test karra.


from google.genai import types

from llms.usage import (
    compute_footprint,
    estimate_content_tokens,
    estimate_tokens,
    extract_usage,
    sum_usage,
)
from models.schemas import LLMCallRecord, UsageSnapshot

USER_25 = "x" * 87            # ceil(87 / 3.5) = 25 tokens
TAIL_140 = types.Content(     # ceil(490 / 3.5) = 140 tokens
    role="model", parts=[types.Part(text="y" * 490)]
)


def make_response(prompt=None, output=None, thoughts=None, cached=None, total=None):
    # Create a mock response object with usage metadata for testing purposes.
    meta = SimpleNamespace(
        prompt_token_count=prompt,
        candidates_token_count=output,
        thoughts_token_count=thoughts,
        cached_content_token_count=cached,
        tool_use_prompt_token_count=None,
        total_token_count=total,
    )
    return SimpleNamespace(usage_metadata=meta)


def make_call(iteration, prompt, output, source="api"):
    # Create a mock LLMCallRecord for testing purposes, with specified iteration, prompt and output token counts, and source.

    return LLMCallRecord(
        iteration=iteration,
        usage=UsageSnapshot(prompt_tokens=prompt, output_tokens=output, source=source),
        latency_ms=100,
    )


def test_estimate_tokens_basics(): # Test the basic functionality of the estimate_tokens function with various input strings.
    assert estimate_tokens("") == 0
    assert estimate_tokens("x" * 7) == 2
    assert estimate_tokens("🌦️ +29°C") > 0  # emoji pe crash nahi


def test_estimate_content_tokens_counts_function_parts():
    call = types.Content(
        role="model",
        parts=[types.Part(function_call=types.FunctionCall(name="weather", args={"city": "Vizag"}))],
    ) # Test that estimate_content_tokens correctly counts tokens in function call parts of a Content object.
    assert estimate_content_tokens(call) > 0


def test_extract_usage_from_api(): # Test that extract_usage correctly extracts usage information from a response object with usage metadata.
    usage = extract_usage(make_response(3989, 19, total=4008))
    assert usage.source == "api"
    assert (usage.prompt_tokens, usage.output_tokens, usage.total_tokens) == (3989, 19, 4008)
    assert usage.thoughts_tokens is None and usage.cached_tokens is None


def test_extract_usage_without_metadata_uses_fallback(): # Test that extract_usage falls back to provided estimates when usage metadata is missing from the response object.
    usage = extract_usage(SimpleNamespace(usage_metadata=None), 100, 20)
    assert usage.source == "estimated"
    assert (usage.prompt_tokens, usage.output_tokens) == (100, 20)


def test_extract_usage_with_missing_prompt_uses_fallback(): # Test that extract_usage falls back to provided estimates when the prompt token count is missing from the usage metadata.
    usage = extract_usage(make_response(prompt=None, output=5), 100, 20)
    assert usage.source == "estimated"


def test_footprint_single_call(): # Test that compute_footprint correctly computes the token footprint for a single LLM call with user input.
    assert compute_footprint([make_call(1, 1200, 80)], USER_25) == (105, "api")


def test_footprint_tool_turn(): # Test that compute_footprint correctly computes the token footprint for multiple LLM calls in a turn, including user input.
    calls = [make_call(1, 1200, 40), make_call(2, 1900, 80)]
    assert compute_footprint(calls, USER_25) == (805, "api")


def test_footprint_awaiting_with_tail(): # Test that compute_footprint correctly computes the token footprint for multiple LLM calls in a turn, including user input and tail content.
    calls = [make_call(1, 1200, 40), make_call(2, 1900, 60)]
    assert compute_footprint(calls, USER_25, tail_contents=[TAIL_140]) == (925, "api")


def test_footprint_negative_delta_is_clamped(): # Test that compute_footprint correctly handles cases where the prompt token count decreases between calls, clamping the delta to zero.
    calls = [make_call(1, 2000, 10), make_call(2, 1500, 10)]
    assert compute_footprint(calls, USER_25) == (35, "api")


def test_footprint_falls_back_to_estimate_when_usage_missing(): # Test that compute_footprint falls back to estimates when usage information is missing from the LLM calls, using turn_contents for estimation.
    calls = [make_call(1, 100, 20, source="estimated")]
    turn = [
        types.Content(role="user", parts=[types.Part(text="x" * 70)]),   # 20
        types.Content(role="model", parts=[types.Part(text="y" * 35)]),  # 10
    ]
    assert compute_footprint(calls, USER_25, turn_contents=turn) == (30, "estimated")


def test_footprint_with_no_calls_uses_estimate(): # Test that compute_footprint correctly estimates the token footprint when there are no LLM calls, using turn_contents for estimation.
    turn = [types.Content(role="user", parts=[types.Part(text="x" * 35)])]
    assert compute_footprint([], USER_25, turn_contents=turn) == (10, "estimated")


def test_sum_usage(): # Test that sum_usage correctly aggregates usage totals across multiple LLM call records.
    calls = [make_call(1, 1200, 40), make_call(2, 1900, 80)]
    totals = sum_usage(calls)
    assert totals.call_count == 2
    assert totals.prompt_tokens_sum == 3100
    assert totals.output_tokens_sum == 120
    assert totals.llm_latency_ms_sum == 200