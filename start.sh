#!/bin/bash

# Get the current directory of the script
CURRENT_DIR=$(pwd)

# Open a new terminal window and start Ollama
echo "Starting Ollama model in a new terminal..."
osascript <<EOF
tell application "Terminal"
    do script "cd $CURRENT_DIR && ollama run llama3.2"
end tell
EOF

# Open another terminal window and start the Python chat UI
echo "Starting Python chat UI in another terminal..."
osascript <<EOF
tell application "Terminal"
    do script "cd $CURRENT_DIR && python chat_ui.py"
end tell
EOF
