from openai import OpenAI
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

# NOTE Lecture number 140

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
tools = [  # ye tool ek list hai jisme ek dic diye, ye dic nested hai jo gemini ke server pe jaati, model isku dekke hi response ka format decide karta, basically ye demand declaration note hai
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

def weather(city:str) -> str: # ye ek function hai jo specially weather api ku use karne aur result return karne use hora, iska return apan further model [line 80-88] ku resend karre
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
        history.append( # as usual, apna req bi history me append karre
            {
                "role": "user",
                "content": convo
            }                   
        )
        try: 
            response = client.chat.completions.create(
                model="gemini-3.1-flash-lite",
                messages=history,
                tools=tools # yahan jab ek api call hui, is block me model ku specify kare ki uske paas ek available tool (line[46]) hai aur woh tool ka ek recoomded design (line[20]) bi hai
            )       
            message = response.choices[0].message # message me kya load hua woh line 115 pe dek sakte
        except Exception as ew:
            print(ew)
            continue
        if message.tool_calls : # agar message.tool_call none nahi hai as case 2 - line [122] toh ander jao
            
            # gemini ke SDKs api ke through aaye json data ku object me convert kardete, isiliye apan message ke ander jo tool_calls ki value hai access karpare using dot. same happend at line80
            # NOTE : read line 127 till end to understand internal working of following code block
            tools_call = message.tool_calls[0] # .tool_calls itself ek dic/list banta as shown at 127, jo ab tools_call namke variable me load hua
            function_name = tools_call.function.name # jaise apan tools me demand kare the, model apne query ku interpret and determine kara, aur agar weather ki baat hui toh function.name me weather word rakdiya
            arguments = json.loads(tools_call.function.arguments)  # arguments me city ke details dalna aur usekar pane ke liye obj ku json me convert kare using json.load, isse line 84 kane aasani se 
            # city deke input city name (eg:Hyderabad, Pune) access karle sakte jo further api function me dia gaya
            if function_name == "weather":
                result = weather(arguments["city"]) # result me apne api function ka output dale, function ku parameter me key diye as city aur value mangaliye
                history.append(message) # jo bi decision,data model liya aur banaya tha, ab history me register hota, taki ai ku context loss na ho
            history.append( # tools ki activity, return values etc ab register hue by specifying new role tool jiski help se model ku pata rehta kon kya kara, 
                           #yahan result ek weather nam ka tool laya blk mention diye model ku
                {
                    "role": "tool",
                    "tool_call_id" : tools_call.id,
                    "content" : result
                }
            ) # ab jab history me reg kare ki current tem wagera kya hora , toh model ku current history deke run karaye, taki unne jawab print karna aur add bi karlena history me
            second_resp = client.chat.completions.create(
                model = "gemini-3.1-flash-lite",
                messages=history,
            )
            answer = second_resp.choices[0].message.content # answer me message ke ander wale content which is actuall response string made by model. woh save hua jo aaage print hua
            
            print(f"Irshard v2: "+ answer)
            history.append( # model khud kya kara, woh bi registered rakhe history me jo unne har call pe padta aur context se relevant rehta
            {
                "role": "assistant",
                "content": answer
            }
        )
        else : # ye case 1 hai, jahan weather ki baat nai hui aur model none mark kara tool_call ku , isse normal convo maintain hua aur append bi hua history me
            print(f"Irshard v2: "+ message.content)
            history.append(
                {
                "role": "assistant",
                "content": message.content
                }
            )   
                       
main() # function call kare
    
    # in case if apan weather ki baat nai chede, toh model message ke ander toolcall none mark kardeta like : 
    # message ke ander following block hai, which includes all decision that model made, like no weather talk so model has marked "tool_call = none" 
#     ChatCompletionMessage(
#     content="Hello! How can I help you today?",
#     role="assistant",
#     function_call=None,
#     tool_calls=None
# )
# case 2: apan weather ki baat kare, ya puche ki x place pe kya weather hai current, toh model message me woh toolcall ku valid mark karke ander bada karta like following aur unme data dalta
# ChatCompletionMessage(
#     content=None,
#     role="assistant",
#     function_call=None,
#     tool_calls=[
#         ChatCompletionMessageToolCall(
#             id="call_12345xyz",
#             type="function",
#             function=Function(
#                 arguments='{"city": "Delhi"}', 
#                 name="weather"
#             )
#         )
#     ]
# )

