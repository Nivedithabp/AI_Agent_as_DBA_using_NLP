import requests
import json
from mongo_operations import log_chat, log_action, perform_mongo_operation

# LLaMA API endpoint
LLAMA_API_URL = "http://localhost:11434/api/generate"

def process_with_llama(user_input):
    """
    Sends the user input to the LLaMA API for natural language processing
    to extract structured data like action, key, and value.
    """
    try:
        prompt = f"Extract action, key, and value or values from: '{user_input}'. Respond in JSON format."
        print(f"[DEBUG] Prompt sent to LLaMA API: {prompt}")

        response = requests.post(
            LLAMA_API_URL,
            json={"model": "llama3.2", "prompt": prompt},
            stream=True
        )
        response.raise_for_status()

        full_response = ""
        for chunk in response.iter_lines():
            if chunk:
                chunk_data = json.loads(chunk.decode("utf-8"))
                full_response += chunk_data.get("response", "")

        print(f"[DEBUG] Raw response: {full_response}")

        extracted_data_start = full_response.find('{')
        extracted_data_end = full_response.rfind('}')
        if extracted_data_start == -1 or extracted_data_end == -1:
            raise ValueError(f"Failed to parse JSON: {full_response}")

        json_response = full_response[extracted_data_start:extracted_data_end + 1]
        extracted_data = json.loads(json_response)
        print(f"[DEBUG] Extracted data: {extracted_data}")
        return extracted_data

    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] RequestException occurred: {str(req_err)}")
        return {"error": str(req_err)}

    except json.JSONDecodeError as json_err:
        print(f"[ERROR] JSON decoding failed: {str(json_err)}")
        return {"error": "Failed to parse JSON from LLaMA output"}

    except Exception as e:
        print(f"[ERROR] General exception occurred: {str(e)}")
        return {"error": str(e)}

def perform_database_operation(action, key, value=None):
    """
    Perform database operation using MongoDB based on the extracted action.
    """
    result = perform_mongo_operation(action, key, value)
    return result

# if __name__ == "__main__":
#     user_input = "delete the key 'Team01'."
#     extracted_data = process_with_llama(user_input)

#     if "error" in extracted_data:
#         print(f"[ERROR] Failed to process user input: {extracted_data['error']}")
#     else:
#         action = extracted_data.get("action")
#         key = extracted_data.get("key")
#         value = extracted_data.get("value")

#         if action and key:
#             result = perform_database_operation(action, key, value)
#             print(f"Final result: {result}")
#             log_chat(user_input, result)
#             log_action(user_input, "Success" if "Successfully" in result else "Failed")