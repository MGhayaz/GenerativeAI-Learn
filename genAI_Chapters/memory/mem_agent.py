import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
from sentence_transformers import SentenceTransformer
from  mem0 import Memory
import json
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_URI = os.getenv("NEO4J_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
config = { # configuration settings aur credintials do client ku
    "llm": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "gemini-3.1-flash-lite",
            "max_tokens": 1024,
        },
    },

    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1",
            "embedding_dims": 384,
        },
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "irshard_memory",
            "embedding_model_dims": 384,
        },
    },

    "graph_store": { # this does not works and get recorgnsised because of our weak llm model and lack of support from mem0 for graph-store
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URI,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
        },
    },
}
mem_client = Memory.from_config(config) # client banao aur config do
while(True):
    user_input = input("💣 YOU: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    mem_search_memory = mem_client.search( # .search me jo bi query dete, usse relevant memory return karta, filter bas ek id hai , id se assiciate memory deta
        query=user_input,
        filters={
        "user_id": "ghayaz"
        }
    )
    memories = [ # yahan jo mem client apni query padke relevant data laya, usku id aur memory word se oder dere taki apna llm usku ache se samaj pana line - 78
    f"ID: {mem.get('id')}\n"
    f"Memory: {mem.get('memory')}"
    for mem in mem_search_memory.get("results", [])
    ]
        

    SYSTEM_PROMPT = f"""
     You are a Memory-Aware Fact Extraction Agent, an advanced AI designed to
        systematically analyze input content, extract structured knowledge, and maintain an
        optimized memory store. Your primary function is information distillation
        and knowledge preservation with contextual awareness.

        Tone: Professional analytical, precision-focused, with clear uncertainty signaling
    {json.dumps(memories, indent=2)}
    """    
    response = client.chat.completions.create( # response create kare by giving system prompt jisme query se related memory hai, llm yahan pada apni memory aur apni query ke uper response banaya
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
    result = mem_client.add( # .add function use hota memory me data add karne, yahan current run ki ai_response aur human query attach kare taki agge ke messages mebi context maintain rehna
        user_id="ghayaz",
        messages=[
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ]
    )