from llms.client import client
from google.genai import types
from config import MODEL_NAME
from prompts import SYSTEM_PROMPT
from tools_schema import TOOLS as tools
import traceback
from llms import history as his
from dotenv import load_dotenv
load_dotenv()
def generate_content(history):
    try :
        response = client.models.generate_content(
            model=MODEL_NAME,  # Gemini me generate_content ke liye sahi model use karein
                contents=history,          # OpenAI ke 'messages' ki jagah 'contents' use hota hai
                config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,    
                tools=tools            # Tools ko config ke andar pass kiya jata hai
                )
            )
    except Exception as ew:
        print(ew)
        traceback.print_exc()
        his.history.pop()
    return response
def generate_followup(history):
    try:
        print("[function unit] final response creation")
        response = client.models.generate_content(
            model=MODEL_NAME, # Sahi stable model identifier use karein
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=tools
            )
        )
        # Agle loop ke liye check karein ki kya model fir se tool call karna chahta hai
        return response
                
    except Exception as ew:
        print(ew)
        traceback.print_exc()
        