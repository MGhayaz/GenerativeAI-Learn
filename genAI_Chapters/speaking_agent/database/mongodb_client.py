from core.config import settings
from pymongo import MongoClient

MONGODB_CONNECTION_STRING =f"mongodb+srv://{settings.mongodb_connection_id}:{settings.mongodb_connection_password}@speaking-agent-cluster.gb3iwdu.mongodb.net/"

mongo_client = MongoClient(MONGODB_CONNECTION_STRING)

conversational_log_database = mongo_client[settings.mongodb_database_name]
regular_collection = conversational_log_database[settings.mongodb_regular_collection_name]
turns_collection = conversational_log_database[settings.mongodb_turns_collection_name]






