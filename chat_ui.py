import gradio as gr
from main import classify_and_respond
from mongo_operations import retrieve_global_chat_history

def chatbot_response(user_input, chat_history=[]):
    """
    Handles user input and returns the updated chat history.
    """
    response = classify_and_respond(user_input)
    chat_history.append((user_input, response))
    return chat_history, chat_history

def load_chat_history():
    """
    Loads persistent chat history from MongoDB.
    """
    history = retrieve_global_chat_history()
    return [(entry["user_message"], entry["agent_response"]) for entry in history]

# Gradio UI
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Type a message...")
    submit_button = gr.Button("Send")
    state = gr.State(load_chat_history())  # Load chat history on initialization

    submit_button.click(
        chatbot_response,
        inputs=[user_input, state],
        outputs=[chatbot, state]
    )

demo.launch()
