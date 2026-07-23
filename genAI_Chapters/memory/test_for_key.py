import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
os.environ["MEM0_TELEMETRY"] = "false"
from  mem0 import Memory
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
config = {
    "version": "v1.1",
    "embedder" : {
        "provider": "openai",
        "config" : {
            "api_key": OPENAI_API_KEY , "model" : "text-embedding-3-small"
        }
    },
    "llm" : {
        "provider": "openai",
        "config" : {
            "api_key": GEMINI_API_KEY , "model" : "gemini-3.1-flash-lite"
        }
    },
    "vector_store" :{
        "provider": "qdrant",
        "config" : {
            "host": "localhost",
            "port" : 6333
        }
    }
}
mem_client = Memory.from_config(config)
user_input = input("Irshard V2: ")

response = client.chat.completions.create(
    model= "gemini-3.1-flash-lite",
    messages=[
        {
            "role": "user",
            "content" : user_input
        }
    ]
)
ai_response = response.choices[0].message.content
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