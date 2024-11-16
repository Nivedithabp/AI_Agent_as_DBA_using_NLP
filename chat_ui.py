from llama_api import process_with_llama
import gradio as gr
from main import classify_and_respond
from mongo_operations import retrieve_global_chat_history
from deep_translator import GoogleTranslator
from langcodes import Language

def chatbot_response(user_input, chat_history=[]):
    try:
        print(f"[DEBUG] User input: {user_input}")
        response = classify_and_respond(user_input)
    except Exception as e:
        response = f"Error processing request: {str(e)}"
    chat_history.append((user_input, response))
    return chat_history, chat_history

def load_chat_history():
    history = retrieve_global_chat_history()
    return [(entry["user_message"], entry["agent_response"]) for entry in history]

# Get all supported languages dynamically
def get_supported_languages():
    return GoogleTranslator().get_supported_languages(as_dict=True)

# Translate content to the selected language
def translate_content(content, language):
    try:
        translator = GoogleTranslator(source='auto', target=language)
        if isinstance(content, str):
            return translator.translate(content)
        elif isinstance(content, list):
            return [translator.translate(item) for item in content]
        elif isinstance(content, dict):
            return {key: translator.translate(value) for key, value in content.items()}
    except Exception as e:
        return content  # Fallback to original content in case of error
    
# Function to filter logs based on log level and update language
def filter_and_translate_logs(selected_level, selected_language, all_logs):
    # Simulated log messages for each level
    log_levels = {
        "Info": "Info: This is an informational log.",
        "Debug": "Debug: This is a debug log.",
        "Error": "Error: This is an error log.",
    }
    
    # Filter logs based on the selected level
    filtered_logs = [log for log in all_logs if selected_level in log]
    
    # Translate the logs to the selected language
    translated_logs = translate_content(filtered_logs, selected_language)
    
    return "\n".join(translated_logs)

# Dynamically translate the entire UI based on the selected language
def update_ui_language(selected_language, logs, user_input, submit_button_label):
    translated_logs = translate_content(logs, selected_language)
    translated_user_input_placeholder = translate_content("Type a message...", selected_language)
    translated_submit_button = translate_content("Send", selected_language)
    
    return (
        gr.update(placeholder=translated_user_input_placeholder),
        gr.update(value=translated_logs),
        gr.update(value=translated_submit_button)
    )

# Gradio UI
with gr.Blocks() as demo:

    supported_languages = get_supported_languages()
    
    gr.Markdown("<br><br>", visible=False)
    # Create layout with 3/4 for chatbot and 1/4 for operations
    with gr.Row():
        # Chatbot on the left side (3/4 width)
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Chatbot")
            
            # User Input and Submit Button
            user_input = gr.Textbox(placeholder="Type a message...")
            submit_button = gr.Button("Send")

        # Operations (input, button, and language dropdown) on the right side (1/4 width)
        with gr.Column(scale=1):
            # Language Dropdown
            language_dropdown = gr.Dropdown(
                list(supported_languages.keys()),
                value="en",
                label="Language",
                interactive=True,
            )
            gr.Markdown("<br><br>", visible=False)
            gr.Markdown("<br><br>", visible=False)
            # Log Level Dropdown for filtering logs
            log_dropdown = gr.Dropdown(
                ["Info", "Debug", "Error"], 
                value="Info", 
                label="Filter Logs"
            )
            gr.Markdown("<br><br>", visible=False)
            gr.Markdown("<br><br>", visible=False)
            # Placeholder for logs display
            logs = gr.Textbox(
                placeholder="Filtered logs will appear here...",
                value="Welcome to the log viewer. Here are your logs.",
                lines=5,
            )

    # Sample logs to filter
    all_logs = [
        "Info: This is an informational log.",
        "Debug: This is a debug log.",
        "Error: This is an error log.",
        "Info: Another informational log.",
        "Debug: Another debug log.",
        "Error: Another error log."
    ]
    
    # Wrap all logs in gr.State to pass it as input to the filter_logs function
    logs_state = gr.State(all_logs)

    state = gr.State([])

    # Interactivity for the chatbot
    submit_button.click(
        chatbot_response,
        inputs=[user_input, state],
        outputs=[chatbot, state]
    )
    
    # Interactivity for the log level dropdown to filter logs and update language
    log_dropdown.change(
        filter_and_translate_logs,
        inputs=[log_dropdown, language_dropdown, logs_state],
        outputs=[logs]
    )

    # Update UI language dynamically
    language_dropdown.change(
        update_ui_language,
        inputs=[language_dropdown, logs, user_input, submit_button],
        outputs=[user_input, logs, submit_button]
    )

# Launch the demo
demo.launch()





