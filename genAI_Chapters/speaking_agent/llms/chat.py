import logging
import random
import time
from typing import Any
from google.genai import types
from google.genai.errors import ServerError,ClientError
from core.config import settings
from core.errors import LLMError
from llms.client import get_client_with_index
from llms.usage import estimate_content_tokens, extract_usage
from models.schemas import LLMCallRecord, UsageSnapshot
from prompts.system import SYSTEM_PROMPT
from tools.schema_builder import build_gemini_tools

logger = logging.getLogger(__name__)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
TOOLS = build_gemini_tools()


def _estimate_response_tokens(response: Any) -> int:
    candidates = response.candidates or []
    content = candidates[0].content if candidates else None
    return estimate_content_tokens(content) if content else 0


def _build_call_record(
    response: Any,
    history: Any,
    iteration: int,
    latency_ms: int,
    attempts: int,
    key_index: int,
) -> LLMCallRecord:
    usage = extract_usage(response)
    if usage.source == "estimated":
        usage = extract_usage(
            response,
            fallback_prompt_est=sum(estimate_content_tokens(c) for c in history),
            fallback_output_est=_estimate_response_tokens(response),
        )

    candidates = response.candidates or []
    finish_reason = getattr(
        getattr(candidates[0], "finish_reason", None), "name", None
    ) if candidates else None

    return LLMCallRecord(
        iteration=iteration,
        usage=usage,
        latency_ms=latency_ms,
        attempts=attempts,
        finish_reason=finish_reason,
        key_index=key_index,
        function_call_count=len(response.function_calls or []),
    )

def _generate_llm_response(history: Any,iteration: int,) -> tuple[Any, LLMCallRecord]: # Purpose : Generate a response from the LLM, handling retries and logging usage information.
    max_retries = settings.llm_max_retries
    started = time.perf_counter()

    for attempt in range(max_retries + 1): # Purpose : Retry the request up to max_retries times in case of retryable errors.
        client, key_index = get_client_with_index() # Purpose : Get a Gemini client and the index of the API key to use for this request, using round-robin selection.
        try:
            response =  client.models.generate_content(
                model=settings.model_name, # Gemini me generate_content ke liye sahi model use karein
                contents=history, # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=TOOLS, # Tools ko config ke andar pass kiya jata hai, and also jabtak agent apna kaam poura nahi karta, unne bada text jaise user ku present kiya jata woh har tool call pe nahi banata, ek turn ke poure tool call hue baad last me response.text banata, jabtak bas response.functioncalls barte rehta
                    temperature=settings.model_temperature
                ),
            )

        except (ServerError,ClientError) as exc:
            status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)

            if status_code not in RETRYABLE_STATUS_CODES:
                logger.exception("Non-retryable Gemini server error: %s",status_code,
                )
                raise LLMError("Gemini server request failed.") from exc

            if attempt >= max_retries:
                logger.error("Gemini request failed after %s retries. Status: %s",
                    max_retries,
                    status_code,
                    exc_info=True,
                )
                raise LLMError("Gemini service is temporarily unavailable.") from exc

            delay = min(
                settings.llm_retry_base_delay * (2 ** attempt),
                settings.llm_retry_max_delay,
            )

            # Add jitter to prevent synchronized retries.
            delay += random.uniform(0, 0.5)

            logger.warning( # purpose : agar Gemini API key limit exceed ho jaye toh retry karein, aur retry ke time pe log karein
                "Gemini returned %s. Retry %s/%s in %.2f seconds.",
                status_code,
                attempt + 1,
                max_retries,
                delay,
            )
            time.sleep(delay)

        except Exception as exc:
            logger.exception("Unexpected Gemini API error")
            raise LLMError("Failed to generate LLM response.") from exc

        else: # Purpose : Build the call record for successful responses
            latency_ms = int((time.perf_counter() - started) * 1000)
            try:
                record = _build_call_record(
                    response, history, iteration, latency_ms, attempt + 1, key_index
                )
            except Exception:
                # measurement kabhi turn ko nahi maarni chahiye
                logger.exception("Failed to build LLM call record")
                record = LLMCallRecord(
                    iteration=iteration,
                    usage=UsageSnapshot(source="estimated"),
                    latency_ms=latency_ms,
                    attempts=attempt + 1,
                    key_index=key_index,
                )
            return response, record
    raise LLMError("Gemini request failed.")
# Jo naya hai: latency_ms retries ka wait milake total wall time hai, attempts retry count, key_index us attempt ka jo successful hua, aur status_code ke liye getattr fallback (SDK version ke hisaab se attribute ka naam alag ho sakta hai).



def generate_content(history: Any, iteration: int = 1) -> tuple[Any, LLMCallRecord]:
    return _generate_llm_response(history,iteration)


def generate_followup(history: Any, iteration: int = 1) -> tuple[Any, LLMCallRecord]:
    logger.info("Generating follow-up LLM response")
    return _generate_llm_response(history,iteration)
