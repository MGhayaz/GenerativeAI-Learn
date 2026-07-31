from client import get_genai_client,types
from config import MODEL_NAME
from prompts import SYSTEM_PROMPT
from history import history
from tools_schema import types_Tool
def generate_content():
    response = get_genai_client().models.generate_content(
                    model=MODEL_NAME,  # Gemini me generate_content ke liye sahi model use karein
                        contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                        config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,    
                        tools=types_Tool()            # Tools ko config ke andar pass kiya jata hai
                        )
                    )
    return response
def generate_followup():
    pass
        