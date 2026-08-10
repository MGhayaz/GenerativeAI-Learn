from llms.client import client
from google.genai import types
from config import MODEL_NAME
from prompts import SYSTEM_PROMPT
from tools_schema import TOOLS

def generate_content(history):
    try :
        response = client.models.generate_content(
            model=MODEL_NAME,  # Gemini me generate_content ke liye sahi model use karein
                contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,    
                tools=TOOLS            # Tools ko config ke andar pass kiya jata hai
                )
            )
        return response
    except Exception as e:
        raise RuntimeError("Failed to generate LLM response") from e
def generate_followup(history):
    try:
        print("[function unit] final response creation")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=TOOLS,
            ),
        )

        return response

    except Exception as e:
        raise RuntimeError(
            "Failed to generate follow-up LLM response"
        ) from e
        