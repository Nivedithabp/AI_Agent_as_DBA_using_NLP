from llama_api import process_with_llama
import gradio as gr
from main import classify_and_respond , classify_and_respond_with_slots
from mongo_operations import retrieve_global_chat_history
from deep_translator import GoogleTranslator
from langcodes import Language


# Function to handle chatbot response with slots
def chatbot_response_with_slots(user_input, chat_history=[], slots={}, selected_language="en"):
    """
    Handles the chatbot response using slots and translates the response
    based on the selected language from the dropdown.
    """
    try:
        print(f"[DEBUG] User input: {user_input}")
        response, updated_slots = classify_and_respond_with_slots(user_input, slots)
        
        # Translate the response to the selected language
        translated_response = translate_content(response, selected_language)
        
        # Append both the input and translated response to chat history
        chat_history.append((user_input, translated_response))
        return chat_history, updated_slots
    except Exception as e:
        response = f"Error processing request: {str(e)}"
        # Translate the error message to the selected language
        translated_response = translate_content(response, selected_language)
        chat_history.append((user_input, translated_response))
        return chat_history, slots


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

html_content = """
<div style="
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 150px; /* Adjusted height for the logo */
    width: 400px; /* Adjusted width for better spacing */
    border-radius: 15px; /* Rounded corners for the logo */
    font-family: Arial, sans-serif;
    text-align: center;">
    <style>
        @media (prefers-color-scheme: dark) {
            .logo-container {
                # background: radial-gradient(circle, #4b79a1, #283e51); /* Subtle gradient for dark mode */
                color: #f5f5f5; /* Soft white for main text */
                text-shadow: 0px 0px 5px rgba(255, 255, 255, 0.6), 0px 0px 10px rgba(0, 255, 150, 0.4), 0px 0px 15px rgba(0, 150, 255, 0.3);
            }
            .tagline {
                color: rgba(255, 255, 255, 0.7); /* Subtle white color for tagline */
            }
        }
        @media (prefers-color-scheme: light) {
            .logo-container {
                # background: radial-gradient(circle, #e0eafc, #cfdef3); /* Soft blue gradient for light mode */
                color: #283e51; /* Dark text for better contrast in light mode */
                text-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2), 0px 0px 10px rgba(0, 255, 150, 0.4), 0px 0px 15px rgba(0, 150, 255, 0.3);
            }
            .tagline {
                color: rgba(40, 62, 81, 0.7); /* Subtle dark color for tagline */
            }
        }
    </style>
    <div class="logo-container" style="padding: 20px; border-radius: 15px;">
        <div style="display: flex; justify-content: center; align-items: baseline; gap: 5px; margin-bottom: 10px;">
            <span style="font-size: 2.5em;">B</span>
            <span style="font-size: 2.3em;">a</span>
            <span style="font-size: 2em;">c</span>
            <span style="font-size: 1.8em;">k</span>
            <span style="font-size: 1.5em;">O</span>
            <span style="font-size: 1.8em;">P</span>
            <span style="font-size: 2em;">S</span>
            <span style="font-size: 1.8em; color: #00d4ff;">.</span>
            <span style="font-size: 2.3em;">A</span>
            <span style="font-size: 2.5em;">I</span>
        </div>
        <div class="tagline" style="
            font-size: 1em;
            text-align: center;
            margin-top: 5px;
            font-style: italic;">
            effortless backend control powered by AI
        </div>
    </div>
</div>
"""

# Gradio UI
with gr.Blocks() as demo:

    backups_ai_title = gr.HTML(html_content)
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

    # state = gr.State([])

    # # Interactivity for the chatbot
    # submit_button.click(
    #     chatbot_response,
    #     inputs=[user_input, state],
    #     outputs=[chatbot, state]
    # )
    
    chat_history_state = gr.State([])
    slot_state = gr.State({"action": None, "key": None, "value": None, "from": None, "to": None})

    submit_button.click(
    chatbot_response_with_slots,
    inputs=[user_input, chat_history_state, slot_state, language_dropdown],
    outputs=[chatbot, slot_state]  # Updates the chatbot with the translated chat history
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