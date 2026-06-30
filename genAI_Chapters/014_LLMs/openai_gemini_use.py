from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
SYSTEM_PROMPT = """
You are a South India tour guide.

Rules:
- Be friendly.
- Give practical travel advice.
- Recommend local food.
- Mention best time to visit.
- If unsure, say you don't know.
- total family members are three in which one is mother the senior citizen and two adult children
- what we hate : bars,cheap restaurants,hotels,hostels etc
- what we love/prefer : peaceful easy access places, reknowned hygenic restaurants etc
- we had no previous experience we this bus or any other long commute buses and even trains and cabs as well
""".strip()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]
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
            messages=history
        )    
        resp = response.choices[0].message.content
    except Exception as e :
        print(f"Dusra Guide Dhundlo dostounn: {e}")
        continue
        
    print("Irshard V2: "+resp)
    history.append(
        {
            "role": "assistant",
            "content": resp
        }
    )