import json
from deep_translator import GoogleTranslator


def read_json(filepath):
    """
    Reads a JSON file and returns its content as a dictionary.
    """
    with open(filepath, 'r', encoding='utf-8') as input_file:
        action_mapping_dict = json.load(input_file)
    return action_mapping_dict


def normalize_action(action, action_mapping_dict):
    """
    Maps synonyms and multilingual actions to core actions using a provided mapping dictionary.
    """
    return action_mapping_dict.get(action.lower(), None)


def translate_response(response, target_language):
    """
    Translates a response to the target language.
    """
    try:
        translator = GoogleTranslator(source="auto", target=target_language)
        return translator.translate(response)
    except Exception as e:
        print(f"[ERROR] Translation failed: {str(e)}")
        return response  # Fallback to the original response
