from llms.client import get_client
from google.genai import types
from core.config import settings
from prompts.system import SYSTEM_PROMPT
from tools.schema_builder import build_gemini_tools
from core.errors import LLMError
from google.genai.errors import ServerError,ClientError
import random
import time
from typing import Any
import logging
logger = logging.getLogger(__name__)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
TOOLS = build_gemini_tools()

def _generate_llm_response(history: Any) -> Any:
    max_retries = settings.llm_max_retries

    for attempt in range(max_retries + 1):
        try:
            return get_client().models.generate_content(
                model=settings.model_name, # Gemini me generate_content ke liye sahi model use karein
                contents=history, # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=TOOLS, # Tools ko config ke andar pass kiya jata hai
                    temperature=settings.model_temperature
                ),
            )

        except (ServerError,ClientError) as exc:
            status_code = exc.status_code

            if status_code not in RETRYABLE_STATUS_CODES:
                logger.exception(
                    "Non-retryable Gemini server error: %s",
                    status_code,
                )
                raise LLMError(
                    "Gemini server request failed."
                ) from exc

            if attempt >= max_retries:
                logger.error(
                    "Gemini request failed after %s retries. Status: %s",
                    max_retries,
                    status_code,
                    exc_info=True,
                )
                raise LLMError(
                    "Gemini service is temporarily unavailable."
                ) from exc

            delay = min(
                settings.llm_retry_base_delay * (2 ** attempt),
                settings.llm_retry_max_delay,
            )

            # Add jitter to prevent synchronized retries.
            delay += random.uniform(0, 0.5)

            logger.warning(
                "Gemini returned %s. Retry %s/%s in %.2f seconds.",
                status_code,
                attempt + 1,
                max_retries,
                delay,
            )

            time.sleep(delay)

        except Exception as exc:
            logger.exception("Unexpected Gemini API error")
            raise LLMError(
                "Failed to generate LLM response."
            ) from exc

    raise LLMError("Gemini request failed.")



def generate_content(history: Any) -> Any:
    return _generate_llm_response(history)


def generate_followup(history: Any) -> Any:
    logger.info("Generating follow-up LLM response")
    return _generate_llm_response(history)
