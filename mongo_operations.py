import pymongo
from datetime import datetime

# MongoDB connection
MONGO_URI = "url"
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


def count_user_records():
    """
    Returns the number of records present in the user table.
    """
    count = user_table.count_documents({})
    return count


def retrieve_success_logs():
    """
    Retrieves logs with 'success' status from MongoDB.
    """
    return list(logs_collection.find({"status": "Success"}, {"_id": 0}).sort("timestamp", -1).limit(10))

def retrieve_failed_logs():
    """
    Retrieves logs with 'failed' status from MongoDB.
    """
    return list(logs_collection.find({"status": "Failed"}, {"_id": 0}).sort("timestamp", -1).limit(10))

def retrieve_all_logs():
    """
    Retrieves all logs from MongoDB.
    """
    return list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))

def count_success_logs():
    """
    Returns the count of logs with 'Success' status.
    """
    success_count = logs_collection.count_documents({"status": "Success"})
    return success_count

def count_failed_logs():
    """
    Returns the count of logs with 'Failed' status.
    """
    failed_count = logs_collection.count_documents({"status": "Failed"})
    return failed_count    

def perform_mongo_operation(action, key=None, value=None):
    """
    Performs the requested database operation (insert, update, delete, get, give/select) in the MongoDB user table.
    """
    try:
        # Handle 'insert' operation
        if action.lower() in ["insert", "add", "append", "include", "place"]:
            if user_table.find_one({"key": key}):
                return f"Key '{key}' already exists in the user table."
            user_table.insert_one({"key": key, "value": value, "created": datetime.now(), "updated": datetime.now()})
            return f"Successfully inserted key '{key}' with value '{value}' into the user table."

        # Handle 'update' operation
        elif action.lower() in ["update", "change", "modify", "edit"]:
            if not user_table.find_one({"key": key}):
                return f"Key '{key}' does not exist in the user table."
            user_table.update_one({"key": key}, {"$set": {"value": value, "updated": datetime.now()}})
            return f"Successfully updated key '{key}' with value '{value}' in the user table."

        # Handle 'delete' operation
        elif action.lower() in ["delete", "remove", "cancel", "cut", "erase"]:
            if not user_table.find_one({"key": key}):
                return f"Key '{key}' does not exist in the user table."
            user_table.delete_one({"key": key})
            return f"Successfully deleted key '{key}' from the user table."

        # Handle 'get' operation
        elif action.lower() in ["get", "find", "fetch"]:
            document = user_table.find_one({"key": key}, {"_id": 0})  # Exclude the MongoDB-generated _id
            if not document:
                return f"Key '{key}' does not exist in the user table."
            return f"Retrieved value for key '{key}': {document.get('value', 'No value found')}."

        # Handle 'give' or 'select' operation (fetch multiple records or a range)
        elif action.lower() in ["give", "select"]:
            documents = list(user_table.find({}, {"_id": 0}))  # Fetch all records, exclude the MongoDB-generated _id
            if not documents:
                return "No records found in the user table."
            return f"Retrieved records: {documents}"

        # Handle unsupported actions
        else:
            return f"Unsupported action: {action}"

    except Exception as e:
        return f"[ERROR] An error occurred while performing the {action} operation: {str(e)}"
