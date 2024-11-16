from llama_api import process_with_llama, perform_database_operation
from mongo_operations import log_chat, log_action

def classify_and_respond(user_input):
    print(f"[DEBUG] classify_and_respond received input: {user_input}")

    extracted_data = process_with_llama(user_input)
    print(f"[DEBUG] Data extracted by LLaMA API: {extracted_data}")

    if "error" in extracted_data:
        return f"Error: {extracted_data['error']}"

    action = extracted_data.get("action")
    key = extracted_data.get("key")
    value = extracted_data.get("value")

    if not action or not key:
        return "[ERROR] Missing action or key in extracted data."

    db_result = perform_database_operation(action, key, value)
    log_chat(user_input, db_result)
    log_action(user_input, "Success" if "Successfully" in db_result else "Failed")
    return db_result
