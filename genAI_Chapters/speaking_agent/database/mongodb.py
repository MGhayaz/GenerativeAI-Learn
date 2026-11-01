from core.config import settings
from pymongo import MongoClient

MONGODB_CONNECTION_STRING =f"mongodb+srv://mohammedghayaz60_db_user:{settings.mongodb_connection_password}@speaking-agent-cluster.gb3iwdu.mongodb.net/"

mongo_client = MongoClient(MONGODB_CONNECTION_STRING)
io = mongo_client.speaking_agent_conversation_logs.list_collection_names()
print(io)

databases = mongo_client.list_database_names()
print(f"databases names : {databases}")
collection_gallery = mongo_client.speaking_agent_conversation_logs
print(f"database {databases[0]} has following collection : {collection_gallery.list_collection_names()}")


