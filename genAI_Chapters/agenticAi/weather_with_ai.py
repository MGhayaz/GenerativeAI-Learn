from openai import OpenAI
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()
SYSTEM_PROMPT = """You are a helpful AI assistant.
You have access to external tools.
When the user asks about weather, forecasts, temperature, rain, humidity, or other weather-related information that requires current or future data:
- Use the weather tool.
- Extract the location from the user's request.
- If the location is missing, ask the user for it.
- Do not guess weather information.
- After receiving the tool result, answer naturally using the returned data.
- Never invent weather conditions."""
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "weather",
            "description": "Get current weather of a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

def weather(city:str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    try : 
        response = requests.get(url)
        return f"{response.text}"
    except Exception as e :
        return f"something went wrong : {e}"
    
def main():    
    while True:
        convo = input("YOU :  ")
        if convo.lower().strip() in ["exit", "band hojao","bye"]:
            print("Irshard V2: Acha waqt bacha raha toh phir milinge")
            break
        history.append(
            {
                "role": "user",
                "content": convo
            }
        )
        try: 
            response = client.chat.completions.create(
                model="gemini-3.1-flash-lite",
                messages=history,
                tools=tools
            )       
            message = response.choices[0].message
        except Exception as ew:
            print(ew)
            continue
        if message.tool_calls :
            tools_call = message.tool_calls[0]
            function_name = tools_call.function.name
            arguments = json.loads(tools_call.function.arguments)
            if function_name == "weather":
                result = weather(arguments["city"])
                history.append(message)
            history.append(
                {
                    "role": "tool",
                    "tool_call_id" : tools_call.id,
                    "content" : result
                }
            )
            second_resp = client.chat.completions.create(
                model = "gemini-3.1-flash-lite",
                messages=history,
            )
            answer = second_resp.choices[0].message.content
            
            print(f"Irshard v2: "+ answer)
            history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
        else :
            print(f"Irshard v2: "+ message.content)
            history.append(
                {
                "role": "assistant",
                "content": message.content
                }
            )   
                       
main()       
    
    