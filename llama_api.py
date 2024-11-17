import requests
import json
from mongo_operations import perform_mongo_operation

LLAMA_API_URL = "http://localhost:11434/api/generate"

def process_with_llama(user_input):
    try:
        prompt = f"Extract action, key, and value from: '{user_input}'. Respond in JSON format."
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

        print(f"[DEBUG] Raw response from LLaMA API: {full_response}")

        # Parse the JSON response
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
        return {"error": f"Request error: {str(req_err)}"}

    except json.JSONDecodeError as json_err:
        print(f"[ERROR] JSON decoding failed: {str(json_err)}")
        return {"error": "Failed to parse JSON from LLaMA output"}

    except Exception as e:
        print(f"[ERROR] General exception occurred: {str(e)}")
        return {"error": str(e)}


# print(process_with_llama("add Team01"))