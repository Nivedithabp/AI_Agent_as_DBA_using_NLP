from utils import read_json, normalize_action, translate_response
from llama_api import process_with_llama, perform_mongo_operation
from mongo_operations import log_chat, log_action
import re

# Load action mappings
ACTION_MAPPING_FILE = "action_mapping.json"
action_mapping_dict = read_json(ACTION_MAPPING_FILE)

# Regex for key validation
VALID_KEY_PATTERN = r"^[a-zA-Z0-9_]{1,15}$"


def classify_and_respond_with_slots(user_input, slots, selected_language="english"):
    """
    Classifies user input, fills slots interactively, and performs DB operations.
    Supports synonyms, slot management, and multi-language responses.
    """
    print(f"[DEBUG] classify_and_respond_with_slots received input: {user_input}")
    print(f"[DEBUG] Current slots: {slots}")

    # Check for "cancel" or "clear" to reset slots
    if user_input.lower() in ["cancel", "clear"]:
        slots.clear()
        return translate_response("Operation canceled. Starting a new conversation.", selected_language), slots

    # Check for "help"
    if user_input.lower() == "help":
        help_message = (
            "Here are some sample prompts you can use:\n"
            "- Add a new key-value pair: 'add team01 value1'\n"
            "- Get the value for a key: 'get team01'\n"
            "- Update a key's value: 'update team01 value2'\n"
            "- Delete a key: 'delete team01'\n"
            "- Cancel the current operation: 'cancel'\n"
            "What would you like to do?"
        )
        slots.clear()
        return translate_response(help_message, selected_language), slots

    # Split input into commands
    commands = re.split(r"\band\b|\n|\.", user_input)
    commands = [cmd.strip() for cmd in commands if cmd.strip()]  # Remove empty or whitespace-only commands

    # Handle multiple commands
    if len(commands) > 1:
        responses = []
        for command in commands:
            response, slots = classify_and_respond_with_slots(command, slots, selected_language)
            responses.append(response)
        return "\n".join(responses), slots

    # Extract slots
    action = slots.get("action")
    key = slots.get("key")
    value = slots.get("value")
    from_value = slots.get("from")
    to_value = slots.get("to")

    # Handle slot filling
    if action and key:
        if not re.match(VALID_KEY_PATTERN, key):
            slots.clear()
            return translate_response(
                f"Invalid key: '{key}'. Keys must only contain letters, numbers, and underscores "
                "and be less than 16 characters long.",
                selected_language,
            ), slots

        if action == "insert" and not value:
            # If value is not yet provided, assume the user input is the value
            slots["value"] = user_input
            value = user_input
        elif action == "update":
            if not from_value and not value:
                # If both 'from' and 'value' are missing, treat input as 'value'
                slots["value"] = user_input
                value = user_input
            elif from_value and not to_value:
                # If 'to' is missing, treat input as 'to'
                slots["to"] = user_input
                to_value = user_input
    else:
        # Classify input to extract action, key, and value
        extracted_data = process_with_llama(user_input)
        print(f"[DEBUG] Data extracted by LLaMA API: {extracted_data}")

        if "error" in extracted_data:
            return translate_response(f"Could not process your input. Error: {extracted_data['error']}", selected_language), slots

        # Normalize action
        action = normalize_action(extracted_data.get("action"), action_mapping_dict)
        key = extracted_data.get("key")
        value = extracted_data.get("value")
        from_value = extracted_data.get("from")
        to_value = extracted_data.get("to")

        # Update slots
        slots.update({"action": action, "key": key, "value": value, "from": from_value, "to": to_value})

    # Validate key again after classification
    if key and not re.match(VALID_KEY_PATTERN, key):
        slots.clear()
        return translate_response(
            f"Invalid key: '{key}'. Keys must only contain letters, numbers, and underscores "
            "and be less than 16 characters long.",
            selected_language,
        ), slots

    # Perform the operation when all slots are filled
    try:
        if action == "delete":
            response = perform_mongo_operation(action, key)
        elif action == "insert":
            if not value:
                return translate_response(
                    "Kindly provide the value for the key to be inserted.", selected_language
                ), slots
            response = perform_mongo_operation(action, key, value=value)
        elif action == "update":
            if from_value and to_value:
                response = perform_mongo_operation(action, key, from_value=from_value, to_value=to_value)
            elif value:
                response = perform_mongo_operation(action, key, value=value)
            else:
                return translate_response(
                    "Kindly provide the value to update the key with.", selected_language
                ), slots
        elif action == "fetch":
            response = perform_mongo_operation(action, key)
        else:
            # Return a message indicating valid operations
            valid_operations = (
            "Supported operations are:\n"
            "- Insert: 'insert key_name value'\n"
            "- Update: 'update key_name value'\n"
            "- Fetch: 'fetch key_name'\n"
            "- Delete: 'delete key_name'"
            )
            return translate_response(
            f"Unsupported action: {action}. {valid_operations}", selected_language
            ), slots

        # Log the action
        log_action(user_input, "Success" if "Successfully" in response else "Failed")

        # Clear slots after successful operation
        slots.clear()

        # Translate response
        return translate_response(response, selected_language), slots

    except Exception as e:
        print(f"[ERROR] Exception in classify_and_respond_with_slots: {e}")
        return translate_response(f"An error occurred: {str(e)}", selected_language), slots
