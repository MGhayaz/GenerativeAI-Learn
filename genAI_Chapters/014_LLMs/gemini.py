from dotenv import  load_dotenv
from google import genai
load_dotenv()
client = genai.Client()

while (True):
    convo = input("YOU :  ")
    if convo.lower().strip() in ["exit", "band hojao","bye"]:
        print("Irshard V2:Acha waqt bacha raha toh phir milinge")
        break
    else: 
        result = client.interactions.create(
            model = "gemini-3.5-flash",
            input = convo
        )
        resp = result.output_text
        print("Irshard V2: "+resp)