import pymongo
from datetime import datetime

# MongoDB connection
MONGO_URI = "mongodb+srv://test:test123456@dba.pqohx.mongodb.net/?retryWrites=true&w=majority&appName=dba"
client = pymongo.MongoClient(MONGO_URI)
db = client["dba"]

# Collections
chat_history_collection = db["chat_history"]
logs_collection = db["logs"]
user_table = db["user"]  # Example table for user data

def log_chat(user_message, agent_response):
    """
    Logs chat messages into MongoDB.
    """
    entry = {
        "user_message": user_message,
        "agent_response": agent_response,
        "timestamp": datetime.now()
    }
    print(f"[DEBUG] Logging chat to MongoDB: {entry}")
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

def perform_mongo_operation(action, key, value=None):
    """
    Performs the requested database operation (insert, update, delete) in the MongoDB user table.
    """
    if action.lower() == "insert":
        if user_table.find_one({"key": key}):
            return f"Key '{key}' already exists in the user table."
        user_table.insert_one({"key": key, "value": value, "created": datetime.now(), "updated": datetime.now()})
        return f"Successfully inserted key '{key}' with value '{value}' into the user table."

    elif action.lower() == "update":
        if not user_table.find_one({"key": key}):
            return f"Key '{key}' does not exist in the user table."
        user_table.update_one({"key": key}, {"$set": {"value": value, "updated": datetime.now()}})
        return f"Successfully updated key '{key}' with value '{value}' in the user table."

    elif action.lower() == "delete":
        if not user_table.find_one({"key": key}):
            return f"Key '{key}' does not exist in the user table."
        user_table.delete_one({"key": key})
        return f"Successfully deleted key '{key}' from the user table."

    else:
        return "Unsupported action."
