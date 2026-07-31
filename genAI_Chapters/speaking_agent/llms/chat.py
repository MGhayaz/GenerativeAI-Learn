from client import get_genai_client
from google.genai import types
from config import MODEL_NAME
from prompts import SYSTEM_PROMPT
from tools_schema import TOOLS
def generate_content(history):
    response = get_genai_client().models.generate_content(
                    model=MODEL_NAME,  # Gemini me generate_content ke liye sahi model use karein
                        contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                        config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,    
                        tools=TOOLS            # Tools ko config ke andar pass kiya jata hai
                        )
                    )
    return response
def generate_followup():
    pass
        