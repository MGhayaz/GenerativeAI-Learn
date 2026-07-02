from fastapi import FastAPI,Body
from ollama import Client
app = FastAPI()
client  = Client(
    host="http://localhost:11434/",
)
@app.get("/")
def read_root():
    return "Live"

@app.post("/chat")
def chat_function(
    message : str = Body(..., description="the message")
):
    resp = client.chat(model="gemma3:4b", messages=[
        {"role":"user", "content":message}
    ])
    return {"response" : resp.message.content}
    