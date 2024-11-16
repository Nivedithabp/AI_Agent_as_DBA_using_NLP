import pymongo
from datetime import datetime

# MongoDB connection
MONGO_URI = "mongodb+srv://test:test123456@dba.pqohx.mongodb.net/?retryWrites=true&w=majority&appName=dba"
client = pymongo.MongoClient(MONGO_URI)
db = client["dba"]

# Collections
chat_history_collection = db["chat_history"]
logs_collection = db["logs"]

def log_chat(user_message, agent_response):
    """
    Logs chat messages into MongoDB.
    """
    entry = {
        "user_message": user_message,
        "agent_response": agent_response,
        "timestamp": datetime.now()
    }
    chat_history_collection.insert_one(entry)

def retrieve_global_chat_history():
    """
    Retrieves all chat history from MongoDB.
    """
    return list(chat_history_collection.find({}, {"_id": 0}).sort("timestamp", 1))

def log_action(task, status):
    """
    Logs actions performed by the AI into MongoDB.
    """
    log_entry = {
        "task": task,
        "status": status,
        "timestamp": datetime.now()
    }
    logs_collection.insert_one(log_entry)
