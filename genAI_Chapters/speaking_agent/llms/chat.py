from llms.client import client
from google.genai import types
from core.config import settings
from prompts.system import SYSTEM_PROMPT
from tools_schema import TOOLS
from core.errors import LLMError
import logging
logger = logging.getLogger(__name__)

def generate_content(history):
    try :
        response = client.models.generate_content(
            model=settings.model_name,  # Gemini me generate_content ke liye sahi model use karein
                contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,    
                tools=TOOLS            # Tools ko config ke andar pass kiya jata hai
                )
            )
        return response
    except Exception as e:
        logger.error("Failed to generate LLM response", exc_info=True)
        raise LLMError("Failed to generate LLM response.") from e
def generate_followup(history):
    try:
        logger.info("Generating follow-up LLM response")

        response = client.models.generate_content(
            model=settings.model_name,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=TOOLS,
            ),
        )

        return response

    except Exception as e:
        logger.error("Failed to generate follow-up LLM response", exc_info=True)
        raise LLMError("Failed to generate follow-up LLM response.") from e
        