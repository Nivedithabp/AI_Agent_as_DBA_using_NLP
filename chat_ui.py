import gradio as gr

# Function for chat logic
def chatbot_response(user_input, chat_history=[]):
    response = f"Echo: {user_input}"
    chat_history.append((user_input, response))
    return chat_history, chat_history

# Create a Gradio Chatbot UI
chat_ui = gr.Chatbot()

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Type a message...")
    submit_button = gr.Button("Send")
    state = gr.State([])

    submit_button.click(
        chatbot_response, 
        inputs=[user_input, state], 
        outputs=[chatbot, state]
    )

demo.launch()

