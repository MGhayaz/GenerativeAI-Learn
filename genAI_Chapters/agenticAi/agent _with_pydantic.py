from openai import OpenAI
import os
import json
import requests
from pydantic import BaseModel
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
def weatherArgs(BaseModel):
    city : str
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
            arguments = weatherArgs.model_validate_json(tools_call.function.arguments)
            if function_name == "weather":
                result = weather(arguments.city)
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
# Pydantic ke pehle
#     LLM ye bhejta tha:
#     '{"city":"Hyderabad"}' jo json.load ki help se apan argument me dalte the, 
#     yahan argument ek dic banke apne ku data bahar deta tha like in previous file<weather_with_api.py> line 85

# pydantic ke baad: 
#     model abi bi yeich '{"city":"Hyderabad"}' bhejra,
    # .model_validate_json ke method hai jo passed args jo json format me hai, usku apne called function<weather_Args> type obj<argument> me dhaldeti
#     arguments = weatherArgs.model_validate_json(tools_call.function.arguments) yahan tools_call.function.arguments == {"city":"Hyderabad"}
#     lekin json.load ki jagae apan .model_validate_json se ander ka data access karre blk unne argument ku weather_Args banara jo ek pydantic object hai : line 17, 82
#     ab jo ki apan weatherArgs define kare aur ander city diye, toh sirf object.properties <eg: argument.city> se bi access kar sakte
#     json.loads() → dict deta hai.
# Pydantic.model_validate_json() → typed Python object deta hai (WeatherArgs), jisme validation already ho chuki hoti hai.

# meku uper wala samaj aaya isliye ye kara
# lecture number 141 - udemy wala tutor jo kara, woh dusra method hai jisku bolte sdk autoparse, unne woh use kara kyuki uskane boht if and else the before enterning tool call, uska code apnse alag hai
# args = response.choices[0].message.parsed
# print(args.city)
