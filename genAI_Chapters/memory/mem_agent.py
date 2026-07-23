import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
from sentence_transformers import SentenceTransformer
from  mem0 import Memory
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
config = {
    "llm": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "gemini-3.1-flash-lite",
            "max_tokens": 1024
        }
    },

    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1",
            "embedding_dims": 384
        }
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "irshard_memory",
             "embedding_model_dims": 384
        }
    }
}
mem_client = Memory.from_config(config)
while(True):
    user_input = input("💣 YOU: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    mem_search_memory = mem_client.search(
        query=user_input,
        filters={
        "user_id": "ghayaz"
        }
    )
    memories = [
    f"ID: {mem.get('id')}\n"
    f"Memory: {mem.get('memory')}"
    for mem in mem_search_memory.get("results", [])
    ]
        

    SYSTEM_PROMPT = f"""
    You are Irshard Bhai.
    Relevant memories about the user:
    {json.dumps(memories, indent=2)}
    Use these memories only if they is need and is relevant for answering the user's current message.
    """    
    response = client.chat.completions.create(
        model= "gemini-3.1-flash-lite",
        messages=[
            {
                            "role": "system",
                            "content" : SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content" : user_input
            }
        ]
    )
    ai_response = response.choices[0].message.content
    print("🗿 Irshard V2 : ",ai_response)
    mem_client.add(
        user_id="ghayaz",
        messages=[
            {
                "role": "user",
                "content" : user_input
            },
            {
                "role": "assistant",
                "content" : ai_response
            }
        ]
    )
    print("Got The Memory Saved")