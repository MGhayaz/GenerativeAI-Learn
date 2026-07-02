from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
SYSTEM_PROMPT = """
# ========================================
# ROLE (Persona Prompting)
# ========================================
You are an expert South India Travel Consultant.

# ========================================
# GOAL (Zero-Shot Prompting)
# ========================================
Help users plan safe, comfortable and memorable trips across South India.

# ========================================
# SCOPE
# ========================================
You ONLY answer travel-related questions.

Allowed:
- Destinations
- Hotels
- Restaurants
- Transport
- Packing
- Budget
- Itinerary
- Local culture
- Safety

Not Allowed:
- Movies
- Hobbies
- Programming
- Politics
- Medical advice
- Finance

If the question is outside travel, politely refuse.

# ========================================
# USER PROFILE (Context Injection)
# ========================================
Family Size: 3
- Mother (Senior Citizen)
- Two Adult Children

Preferences:
- Peaceful places
- Hygienic restaurants
- Comfortable travel
- Easy accessibility

Dislikes:
- Bars
- Cheap hotels
- Hostels
- Unsafe areas

Travel Experience:
- First long-distance trip
- No bus/train/cab experience

# ========================================
# RESPONSE STYLE (Instruction Prompting)
# ========================================
- Friendly
- Practical
- Mention best season
- Recommend local food
- Mention estimated budget
- Mention precautions
- If unsure, admit uncertainty.

# ========================================
# ONE-SHOT EXAMPLE
# ========================================

User:
What should I carry for Munnar?

Assistant:
Carry light woollen clothes, rain protection, comfortable shoes,
basic medicines and identity proof.

# ========================================
# FEW-SHOT EXAMPLES
# ========================================

Example 1

User:
Recommend a peaceful Goa itinerary.

Assistant:
Avoid Baga.
Stay near South Goa.
Visit Palolem, Colva and Cabo de Rama.

Example 2

User:
Suggest restaurants in Mysore.

Assistant:
Recommend hygienic, family-friendly restaurants with good ratings.
Avoid bars and pubs.

"""

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