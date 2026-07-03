from fastapi import FastAPI,Body
from ollama import Client
app = FastAPI() # fastapi ki application banaye, basically jisku bulae usku baithaye takki usse kam le sakna
client  = Client(
    host="http://localhost:11434/", #  Ollama server (localhost:11434) se connect karta.
)
@app.get("/") # Client jab data read/request karta hai tab GET endpoint call hota hai.
def read_root():
    return "Live"

@app.post("/chat")  # Client jab data bhejta hai (jaise chat message), tab POST endpoint use hota hai.
def chat_function(
    message : str = Body(..., description="the message") # # Request body se message receive karke message variable me store karta hai.
):
    resp = client.chat(model="gemma3:4b", messages=[
        {"role":"user", "content":message} # yahan ollama ke inbuild method chat ku call karke, ai model, role, aur user query diye and finally output-of-ai ku resp me dale and later return kare
    ])
    return {"response" : resp.message.content} # fastapi automatically JSON format me serve karta return ku
    