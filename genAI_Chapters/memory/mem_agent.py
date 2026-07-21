from  mem0 import Memory
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
config = {
    "version": "v1.1",
    "embedder" : {
        "provider": "google_genai",
        "config" : {
            "api_key": GEMINI_API_KEY , "model" : "gemini-embedding-2-preview"
        }
    },
    "llm" : {
        "provider": "google_genai",
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
mem_client.