from llama_api import process_with_llama, perform_mongo_operation
from mongo_operations import log_chat, log_action

def classify_and_respond_with_slots(user_input, slots):
    """
    Classifies user input, fills slots interactively, and performs DB operations when slots are filled.
    Supports "cancel" or "clear" to reset the conversation.
    """
    print(f"[DEBUG] classify_and_respond_with_slots received input: {user_input}")
    print(f"[DEBUG] Current slots: {slots}")

    # Check for "cancel" or "clear" to reset the conversation
    if user_input.lower() in ["cancel", "clear"]:
        slots.clear()
        return "Operation canceled. Starting a new conversation.", slots
    # Check for "help" to provide guidance
    if user_input.lower() == "help":
        help_message = (
            "Here are some sample prompts you can use:\n"
            "- Add a new key-value pair: 'add team01 value1'\n"
            "- Get the value for a key: 'get team01'\n"
            "- Update a key's value: 'update team01 value2'\n"
            "- Update conditionally: 'update team01 from value1 to value2'\n"
            "- Delete a key: 'delete team01'\n"
            "- Cancel the current operation: 'cancel'\n"
            "What would you like to do?"
        )
        slots.clear()
        return help_message, slots
    
    # Extract slot data
    action = slots.get("action")
    key = slots.get("key")
    value = slots.get("value")
    from_value = slots.get("from")
    to_value = slots.get("to")

    # If missing slots, use the input to fill them
    if action and key:
        if action.lower() in ["add", "insert"] and not value:
            slots["value"] = user_input
            value = user_input
        elif action.lower() == "update":
            if not from_value and not value:
                # Update expects either `value` or `from`
                slots["value"] = user_input
                value = user_input
            elif from_value and not to_value:
                # Update expects `to` value after `from`
                slots["to"] = user_input
                to_value = user_input
    else:
        # If no ongoing slot filling, classify the input
        extracted_data = process_with_llama(user_input)
        print(f"[DEBUG] Data extracted by LLaMA API: {extracted_data}")

        if "error" in extracted_data:
            return f"Could not process your input. Error: {extracted_data['error']}", slots

        # Update slots with extracted data
        action = extracted_data.get("action")
        key = extracted_data.get("key")
        value = extracted_data.get("value")
        from_value = extracted_data.get("from")
        to_value = extracted_data.get("to")
        slots.update({"action": action, "key": key, "value": value, "from": from_value, "to": to_value})

    # Handle missing slots interactively
    if not action:
        return "What action would you like to perform? (e.g., add, update, delete, get, give)", slots

    if action.lower() in ["get", "give"] and not key:
        return "Please provide the key to retrieve data.", slots

    if action.lower() in ["insert", "add"] and not key:
        return "Kindly provide the key to be inserted.", slots

    if action.lower() in ["insert", "add"] and not value:
        return "Kindly provide the value to be inserted.", slots

    if action.lower() == "update":
        if not from_value and not value:
            return "What value would you like to update the key with?", slots
        if from_value and not to_value:
            return "Please provide the new value (to) for the update.", slots

    # Perform the database operation when all slots are filled
    try:
        if action.lower() == "delete":
            response = perform_mongo_operation(action, key)
        elif action.lower() in ["insert", "add"]:
            response = perform_mongo_operation(action, key, value=value)
        elif action.lower() == "update":
            if from_value and to_value:
                response = perform_mongo_operation(action, key, from_value=from_value, to_value=to_value)
            else:
                response = perform_mongo_operation(action, key, value=value)
        elif action.lower() in ["get", "give" , "select"]:
            response = perform_mongo_operation(action, key)
        else:
            response = f"Unsupported action: {action}"
        # Log the action after database operation
        log_action(user_input, "Success" if "Successfully" in response else "Failed")
        # Clear slots after successful operation
        slots.clear()
        return response, slots

    except Exception as e:
        print(f"[ERROR] Exception in classify_and_respond_with_slots: {e}")
        return f"An error occurred: {str(e)}", slots


# def classify_and_respond_with_slots(user_input, slots):
#     """
#     Classifies user input, fills slots interactively, and performs DB operations when slots are filled.
#     """
#     print(f"[DEBUG] classify_and_respond_with_slots received input: {user_input}")
#     print(slots)
#     # Extract slot data
#     action = slots.get("action")
#     key = slots.get("key")
#     value = slots.get("value")
#     update_from = slots.get("from")
#     update_to = slots.get("to")

#     # If value is pending and no new action is detected, treat input as the missing slot
#     if action and key and not value:
#         print(f"[DEBUG] Filling missing 'value' slot with user input: {user_input}")
#         slots["value"] = user_input
#         value = user_input

#     elif action == "update" and key and not update_from:
#         print(f"[DEBUG] Filling missing 'from' slot with user input: {user_input}")
#         slots["from"] = user_input
#         update_from = user_input

#     elif action == "update" and key and update_from and not update_to:
#         print(f"[DEBUG] Filling missing 'to' slot with user input: {user_input}")
#         slots["to"] = user_input
#         update_to = user_input

#     else:
#         # If no ongoing slot filling, classify the input to determine action
#         extracted_data = process_with_llama(user_input)
#         print(f"[DEBUG] Data extracted by LLaMA API: {extracted_data}")

#         if "error" in extracted_data:
#             return f"Could not process your input. Error: {extracted_data['error']}", slots

#         # Update slots with extracted data
#         action = extracted_data.get("action")
#         key = extracted_data.get("key")
#         value = extracted_data.get("value")
#         update_from = extracted_data.get("from")
#         update_to = extracted_data.get("to")
#         slots.update({"action": action, "key": key, "value": value, "from": update_from, "to": update_to})

#     # Handle missing slots interactively
#     if not action:
#         return "What action would you like to perform? (e.g., add, update, delete, get)", slots

#     if not key:
#         return "Kindly provide the key to proceed.", slots

#     if action.lower() in ["insert", "add"] and not value:
#         return "Kindly provide the value to be inserted.", slots

#     if action.lower() == "update":
#         if not update_from:
#             return "Please provide the current value (from) to update.", slots
#         if not update_to:
#             return "Please provide the new value (to) for the update.", slots

#     # Perform database operation when all slots are filled
#     try:
#         if action.lower() == "delete":
#             response = perform_mongo_operation(action, key)
#         elif action.lower() in ["insert", "add"]:
#             response = perform_mongo_operation(action, key, value=value)
#         elif action.lower() == "update":
#             response = perform_mongo_operation(action, key, update_from=update_from, update_to=update_to)
#         elif action.lower() == "get":
#             response = perform_mongo_operation(action, key)
#         elif action.lower() in ["give", "select"]:
#             response = perform_mongo_operation(action)
#         else:
#             response = f"Unsupported action: {action}"

#         # Clear slots after the operation
#         slots.clear()
#         return response, slots

#     except Exception as e:
#         print(f"[ERROR] Exception in classify_and_respond_with_slots: {e}")
#         return f"An error occurred: {str(e)}", slots


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

    db_result = perform_mongo_operation(action, key, value)
    log_chat(user_input, db_result)
    log_action(user_input, "Success" if "Successfully" in db_result else "Failed")
    return db_result
