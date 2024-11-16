import requests

def llama_api_call(user_input):
    """
    Calls the LLaMA 3.2 API hosted by Ollama to process user input.
    """
    API_URL = "http://localhost:11434/api/v1/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.2",
        "prompt": f"""
        You are a database assistant. Parse the user's input into structured JSON.
        Input: {user_input}
        """
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("content", "{}")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
