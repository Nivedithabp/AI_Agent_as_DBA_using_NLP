from llama_api import process_with_llama
import gradio as gr
from main import classify_and_respond_with_slots
from mongo_operations import retrieve_global_chat_history
from deep_translator import GoogleTranslator
from langcodes import Language
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import json
from faq import get_faq_content
from mongo_operations import retrieve_success_logs, retrieve_failed_logs, retrieve_all_logs, count_user_records, count_success_logs, count_failed_logs
import pandas as pd
import os


# Function to generate the stats graph and scoreboard
def generate_stats_graph():
    # Generate the data
    categories = ['Success', 'Failed', 'Total Records']
    values = [count_success_logs(), count_failed_logs(), count_user_records()]
    colors = ['#1E90FF', '#4682B4', '#5F9EA0']

    data = {"Category": categories, "Value": values}
    graph_path = create_bar_graph(data, "Category", "Value", colors)

    # Generate scoreboard HTML
    scoreboard_html = f"""
    <div style="color: #FFD700; font-size: 24px; background: #1E1E1E; padding: 20px; border-radius: 10px;">
        <h2 style="margin: 0;">Database Record Stats</h2>
        <p>✅ Success: <strong>{values[0]}</strong></p>
        <p>❌ Failed: <strong>{values[1]}</strong></p>
        <p>📋 Total Records: <strong>{values[2]}</strong></p>
    </div>
    """
    
    # Return the updated graph path and scoreboard HTML
    return graph_path, scoreboard_html


# Function to create and save the bar graph with specific colors for categories
def create_bar_graph(data, x_col, y_col, colors):
    df = pd.DataFrame(data)
    
    # Create the plot with a gaming theme
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(df[x_col], df[y_col], color=colors, edgecolor="black")
    
    # Set titles and labels with a gaming font
    ax.set_title("Operations and Records Count", fontsize=18, color="#FFD700", weight="bold")
    ax.set_xlabel(x_col, fontsize=14, color="#00FFFF")
    ax.set_ylabel(y_col, fontsize=14, color="#00FFFF")
    ax.tick_params(axis='x', colors="#FF69B4")
    ax.tick_params(axis='y', colors="#FF69B4")
    ax.set_facecolor("#1E1E1E")  # Dark background for gaming theme
    fig.patch.set_facecolor("#2B2B2B")  # Outer background for the figure

    # Save the figure
    image_path = "gaming_bar_graph.png"
    fig.savefig(image_path, dpi=150)
    plt.close(fig)
    return image_path

# Function to handle the visibility toggling for FAQ and Stats
def toggle_visibility(show_faq, show_stats, section):
    if section == "faq":
        return gr.update(visible=True), gr.update(visible=False), False, True
    elif section == "stats":
        return gr.update(visible=False), gr.update(visible=True), True, False


# Function to handle chatbot response with slots
def chatbot_response_with_slots(user_input, chat_history=[], slots={}, selected_language="english"):
    """
    Handles the chatbot response using slots and translates the response
    based on the selected language from the dropdown.
    """
    try:
        print(f"[DEBUG] User input: {user_input}")
        response, updated_slots = classify_and_respond_with_slots(user_input, slots ,selected_language )
        
        # Translate the response to the selected language
        #translated_response = translate_content(response, selected_language)
        
        # Append both the input and translated response to chat history
        chat_history.append((user_input, response))
        return chat_history, updated_slots
    except Exception as e:
        response = f"Error processing request: {str(e)}"
        # Translate the error message to the selected language
        translated_response = translate_content(response, selected_language)
        chat_history.append((user_input, translated_response))
        return chat_history, slots


# def chatbot_response(user_input, chat_history=[]):
#     try:
#         print(f"[DEBUG] User input: {user_input}")
#         response = classify_and_respond(user_input)
#     except Exception as e:
#         response = f"Error processing request: {str(e)}"
#     chat_history.append((user_input, response))
#     return chat_history, chat_history

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
    
def get_and_filter_logs(selected_level, logs_state, selected_language):
    if selected_level == "success":
        raw_logs = retrieve_success_logs()
    elif selected_level == "failed":
        raw_logs = retrieve_failed_logs()
    else:
        raw_logs = retrieve_all_logs()

    processed_logs = []
    for log in raw_logs:
        task = log['task']
        status = log['status']
        timestamp = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

        processed_log = {
            'status': status,
            'task': task,
            'timestamp': timestamp
        }

        processed_logs.append(processed_log)

    translated_logs = translate_logs(processed_logs, selected_language)
    logs_state = translated_logs
    logs_display = "\n".join([f"{log['timestamp']} : {log['task']}" for log in translated_logs])

    return logs_display, logs_state

def translate_logs(logs, language):
    try:
        translator = GoogleTranslator(source='auto', target=language)
        for log in logs:
            log['task'] = translator.translate(log['task'])
            log['status'] = translator.translate(log['status'])
        return logs
    except Exception as e:
        print(f"Error translating logs: {e}")
        return logs

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
            # FAQ and Stats buttons in a row
            with gr.Row(): 
                faq_button = gr.Button("FAQ")
                stats_button = gr.Button("Stats")

            language_dropdown = gr.Dropdown(
                list(supported_languages.keys()),
                value="english",
                label="Language",
                interactive=True,
            )
            log_dropdown = gr.Dropdown(
                ["Success", "Failed", "All"],  
                label="Filter Logs"
            )
            logs = gr.Textbox(
                label="Logs",
                placeholder="Filtered logs will appear here...",
                value="Welcome to the log viewer. Here are your logs.",
                lines=5,
            )
    
    logs_state = gr.State([])

    # Add Stats and FAQ section dynamically
    with gr.Row():
        with gr.Column(scale=1):
            stats_image = gr.Image(label="Stats Graph", elem_id="stats-graph", height=400, visible=True)
        with gr.Column(scale=1):
            content_display = gr.HTML(label="Scoreboard", visible=True)  # To show FAQ or scoreboard

    # Stats Button to generate and update graph/scoreboard
    stats_button.click(
        generate_stats_graph,
        inputs=[],
        outputs=[stats_image, content_display],  # Updates both graph and scoreboard
    )

    # FAQ Button to replace the stats graph with FAQ content
    faq_button.click(
        lambda: (gr.update(visible=False), gr.update(value=get_faq_content(), visible=True)),
        inputs=[],
        outputs=[stats_image, content_display]  # Replaces graph with FAQ content
    )
    
    # Chatbot functionality
    chat_history_state = gr.State([])
    slot_state = gr.State({"action": None, "key": None, "value": None, "from": None, "to": None})

    submit_button.click(
        chatbot_response_with_slots,
        inputs=[user_input, chat_history_state, slot_state, language_dropdown],
        outputs=[chatbot, slot_state]
    )

    user_input.submit(lambda: "", inputs=[], outputs=[user_input])

    language_dropdown.change(
        update_ui_language,
        inputs=[language_dropdown, logs, user_input, submit_button],
        outputs=[user_input, logs, submit_button],
    )

    log_dropdown.change(
        get_and_filter_logs,
        inputs=[log_dropdown, logs_state, language_dropdown],
        outputs=[logs, logs_state],
    )

# Launch the demo
demo.launch()
