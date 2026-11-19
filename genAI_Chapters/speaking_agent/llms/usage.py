import json
import math
from collections.abc import Sequence
from typing import Any

from google.genai import types

from models.schemas import LLMCallRecord, UsageSnapshot, UsageTotals

DEFAULT_CHARS_PER_TOKEN = 3.5 # Default average number of characters per token, used for estimating token counts from text length.


def estimate_tokens(
    text: str,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
) -> int:
    # Estimate token count from text length. This is a rough approximation and may not match the actual tokenization used by the model.
    if not text:
        return 0
    return math.ceil(len(text) / chars_per_token)


def estimate_content_tokens(
    content: types.Content,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
) -> int:
    # Estimate token count from a Content object, including text and function call parts.
    total = 0
    for part in content.parts or []:
        if part.text:
            total += estimate_tokens(part.text, chars_per_token)
        if part.function_call:
            call = part.function_call
            payload = f"{call.name} {json.dumps(call.args or {}, ensure_ascii=False)}"
            total += estimate_tokens(payload, chars_per_token)
        if part.function_response:
            resp = part.function_response
            payload = (
                f"{resp.name} "
                f"{json.dumps(resp.response or {}, ensure_ascii=False, default=str)}"
            )
            total += estimate_tokens(payload, chars_per_token)
    return total

# NOTE : usage_metadata extract karra inne
def extract_usage(
    response: Any,
    fallback_prompt_est: int = 0,
    fallback_output_est: int = 0,
) -> UsageSnapshot:
    # Extract usage information from a response object, falling back to estimates if necessary.
    """usage_metadata safe read. Prompt count na mile toh estimate + source='estimated'."""
    meta = getattr(response, "usage_metadata", None)
    prompt = getattr(meta, "prompt_token_count", None)

    if prompt is None:
        return UsageSnapshot(
            prompt_tokens=fallback_prompt_est,
            output_tokens=fallback_output_est,
            source="estimated",
        )

    return UsageSnapshot(
        prompt_tokens=prompt,  
        output_tokens=getattr(meta, "candidates_token_count", None) or 0,  # getattr ka kaam hai agar attribute exist nahi karta toh default value return karna, aur agar exist karta hai toh uska value return karna
        thoughts_tokens=getattr(meta, "thoughts_token_count", None),
        cached_tokens=getattr(meta, "cached_content_token_count", None),
        tool_use_prompt_tokens=getattr(meta, "tool_use_prompt_token_count", None),
        total_tokens=getattr(meta, "total_token_count", None),
        source="api",
    )


def compute_footprint(
    calls: Sequence[LLMCallRecord],
    user_text: str,
    tail_contents: Sequence[types.Content] = (),
    turn_contents: Sequence[types.Content] = (),
) -> tuple[int, str]:
    # Compute the total token footprint of a series of LLM calls, including user input and any tail content, returning the total token count and the source of the usage data.
    """F = (P_n - P_1) + U + O_n + E_tail. Usage missing ho toh turn_contents se estimate."""
    first = calls[0] if calls else None
    last = calls[-1] if calls else None

    if (
        first is not None
        and first.usage.source == "api"
        and last.usage.source == "api"
        and first.usage.prompt_tokens is not None
        and last.usage.prompt_tokens is not None
    ):
        tool_part = max(0, last.usage.prompt_tokens - first.usage.prompt_tokens)
        output = last.usage.output_tokens or 0
        user = estimate_tokens(user_text)
        tail = sum(estimate_content_tokens(c) for c in tail_contents)
        return max(1, tool_part + user + output + tail), "api"

    estimated = sum(estimate_content_tokens(c) for c in turn_contents)
    return max(1, estimated), "estimated"


def sum_usage(calls: Sequence[LLMCallRecord]) -> UsageTotals:
    # Sum the usage totals across a sequence of LLM call records, returning a UsageTotals object with aggregated counts.
    totals = UsageTotals()
    for call in calls:
        usage = call.usage
        totals.call_count += 1
        totals.prompt_tokens_sum += usage.prompt_tokens or 0
        totals.output_tokens_sum += usage.output_tokens or 0
        totals.thoughts_tokens_sum += usage.thoughts_tokens or 0
        totals.cached_tokens_sum += usage.cached_tokens or 0
        totals.llm_latency_ms_sum += call.latency_ms
    return totals