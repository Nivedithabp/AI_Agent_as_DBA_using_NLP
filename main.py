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
            "- Update conditionally: 'update team01 from value1 to value2'\n"
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
            slots["value"] = user_input
            value = user_input
        elif action == "update":
            if not from_value and not value:
                slots["value"] = user_input
                value = user_input
            elif from_value and not to_value:
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
            response = perform_mongo_operation(action, key, value=value)
        elif action == "update":
            if from_value and to_value:
                response = perform_mongo_operation(action, key, from_value=from_value, to_value=to_value)
            else:
                response = perform_mongo_operation(action, key, value=value)
        elif action == "fetch":
            response = perform_mongo_operation(action, key)
        else:
            response = f"Unsupported action: {action}"

        # Log the action
        log_action(user_input, "Success" if "Successfully" in response else "Failed")

        # Clear slots after successful operation
        slots.clear()

        # Translate response
        return translate_response(response, selected_language), slots

    except Exception as e:
        print(f"[ERROR] Exception in classify_and_respond_with_slots: {e}")
        return translate_response(f"An error occurred: {str(e)}", selected_language), slots


# from llama_api import process_with_llama, perform_mongo_operation
# from mongo_operations import log_chat, log_action
# import re

# def classify_and_respond_with_slots(user_input, slots):
#     """
#     Classifies user input, fills slots interactively, and performs DB operations when slots are filled.
#     Supports "cancel" or "clear" to reset the conversation.
#     Handles multiple commands separated by "and", "\n", or ".".
#     Validates keys using regex.
#     """
#     print(f"[DEBUG] classify_and_respond_with_slots received input: {user_input}")
#     print(f"[DEBUG] Current slots: {slots}")

#     # Regex pattern for a valid key
#     valid_key_pattern = r"^[a-zA-Z0-9_]{1,15}$"

#     # Check for "cancel" or "clear" to reset the conversation
#     if user_input.lower() in ["cancel", "clear"]:
#         slots.clear()
#         return "Operation canceled. Starting a new conversation.", slots

#     # Check for "help" to provide guidance
#     if user_input.lower() == "help":
#         help_message = (
#             "Here are some sample prompts you can use:\n"
#             "- Add a new key-value pair: 'add team01 value1'\n"
#             "- Get the value for a key: 'get team01'\n"
#             "- Update a key's value: 'update team01 value2'\n"
#             "- Update conditionally: 'update team01 from value1 to value2'\n"
#             "- Delete a key: 'delete team01'\n"
#             "- Cancel the current operation: 'cancel'\n"
#             "What would you like to do?"
#         )
#         slots.clear()
#         return help_message, slots

#     # Split input by multiple delimiters: "and", "\n", "."
#     commands = re.split(r"\band\b|\n|\.", user_input)
#     commands = [cmd.strip() for cmd in commands if cmd.strip()]  # Remove empty or whitespace-only commands

#     if len(commands) > 1:
#         responses = []
#         for command in commands:
#             # Recursively process each command
#             response, slots = classify_and_respond_with_slots(command.strip(), slots)
#             responses.append(response)
#         return "\n".join(responses), slots

#     # Extract slot data
#     action = slots.get("action")
#     key = slots.get("key")
#     value = slots.get("value")
#     from_value = slots.get("from")
#     to_value = slots.get("to")

#     # If missing slots, use the input to fill them
#     if action and key:
#         # Validate key before proceeding
#         if not re.match(valid_key_pattern, key):
#             return (
#                 f"Invalid key: '{key}'. Keys must only contain letters, numbers, and underscores "
#                 "and be less than 16 characters long.",
#                 slots,
#             )

#         if action.lower() in ["add", "insert"] and not value:
#             slots["value"] = user_input
#             value = user_input
#         elif action.lower() == "update":
#             if not from_value and not value:
#                 slots["value"] = user_input
#                 value = user_input
#             elif from_value and not to_value:
#                 slots["to"] = user_input
#                 to_value = user_input
#     else:
#         # If no ongoing slot filling, classify the input
#         extracted_data = process_with_llama(user_input)
#         print(f"[DEBUG] Data extracted by LLaMA API: {extracted_data}")

#         if "error" in extracted_data:
#             return f"Could not process your input. Error: {extracted_data['error']}", slots

#         # Update slots with extracted data
#         action = extracted_data.get("action")
#         key = extracted_data.get("key")
#         value = extracted_data.get("value")
#         from_value = extracted_data.get("from")
#         to_value = extracted_data.get("to")
#         slots.update({"action": action, "key": key, "value": value, "from": from_value, "to": to_value})

#     # Validate the key
#     if key and not re.match(valid_key_pattern, key):
#         slots.clear()
#         return (
#             f"Invalid key: '{key}'. Keys must only contain letters, numbers, and underscores "
#             "and be less than 16 characters long.",
#             slots,
#         )

#     # Handle missing slots interactively
#     if not action:
#         return "What action would you like to perform? (e.g., add, update, delete, get, give)", slots

#     if action.lower() in ["get", "give", "select"] and not key:
#         return "Please provide the key to retrieve data.", slots

#     if action.lower() in ["insert", "add"] and not key:
#         return "Kindly provide the key to be inserted.", slots

#     if action.lower() in ["insert", "add"] and not value:
#         return "Kindly provide the value to be inserted.", slots

#     if action.lower() == "update":
#         if not from_value and not value:
#             return "What value would you like to update the key with?", slots
#         if from_value and not to_value:
#             return "Please provide the new value (to) for the update.", slots

#     # Perform the database operation when all slots are filled
#     try:
#         if action.lower() == "delete":
#             response = perform_mongo_operation(action, key)
#         elif action.lower() in ["insert", "add"]:
#             response = perform_mongo_operation(action, key, value=value)
#         elif action.lower() == "update":
#             if from_value and to_value:
#                 response = perform_mongo_operation(action, key, from_value=from_value, to_value=to_value)
#             else:
#                 response = perform_mongo_operation(action, key, value=value)
#         elif action.lower() in ["get", "give", "select"]:
#             response = perform_mongo_operation(action, key)
#         else:
#             response = f"Unsupported action: {action}"

#         # Log the action after database operation
#         log_action(user_input, "Success" if "Successfully" in response else "Failed")

#         # Clear slots after successful operation
#         slots.clear()
#         return response, slots

#     except Exception as e:
#         print(f"[ERROR] Exception in classify_and_respond_with_slots: {e}")
#         return f"An error occurred: {str(e)}", slots



