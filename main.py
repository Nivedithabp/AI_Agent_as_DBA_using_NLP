from llama_api import llama_api_call
from mongo_operations import log_chat, log_action, retrieve_global_chat_history
from backend_store import KeyValueStore
from intent_classifier import classify_intent

# Initialize key-value store
kv_store = KeyValueStore()

def process_request(user_input):
    """
    Processes user input by converting it into structured tasks and executing them.
    """
    structured_response = llama_api_call(user_input)  # Call LLaMA API

    try:
        tasks = eval(structured_response)  # Convert JSON string to Python list
        results = []
        for task in tasks:
            action = task.get("action")
            table = task.get("table")
            values = task.get("values", {})

            # Execute tasks
            if action == "insert":
                result = kv_store.insert(table, values)
            elif action == "update":
                result = kv_store.update(table, values)
            elif action == "delete":
                result = kv_store.delete(table)
            else:
                result = f"Unsupported action: {action}"
            results.append(result)
            log_action(task, "success")
        return "\n".join(results)
    except Exception as e:
        log_action({"user_input": user_input}, "failed")
        return f"Error processing request: {e}"

def classify_and_respond(user_input):
    """
    Classifies the user's intent and provides the appropriate response.
    """
    intent = classify_intent(user_input)
    if intent == "irrelevant":
        response = "Please ask something related to backend database operations."
    else:
        response = process_request(user_input)

    # Log the interaction
    log_chat(user_input, response)
    return response
