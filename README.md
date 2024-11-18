# AI Agent for Operating a Backend System Using Natural Language

## Project Overview
This project creates an AI agent that interacts with users through natural language to operate a backend system, such as a key-value store. The agent uses a Large Language Model (LLM) to interpret user requests and perform corresponding backend operations like insertion, update, and deletion.
## Demo

https://youtu.be/P32ASsNMB4k?si=aNvr8jFBWz38N-ox
---
## Architecture
![image](https://github.com/user-attachments/assets/21a0d14f-cca0-448d-b5eb-23cfcbbc4aec)

## Prerequisites
1. **Python 3.8+**
2. **Required Libraries**: Install dependencies using the provided requirements file:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ollama LLM Installed**: Ensure Ollama's `llama3.2` model is set up:
   ```bash
   ollama run llama3.2
   ```

---

## Installation & Setup
1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   - Using Python:
     ```bash
     python chat_ui.py
     ```
     Access the application at `http://127.0.0.1:7860`.
   - Using the Shell Script:
     ```bash
     ./start.sh
     ```

---

## Features
### 1. **Natural Language Backend Operations**
   - Interpret user instructions like:
     - _"Insert key 'my.test' with value 'my.value'."_
     - _"Update key 'my.test' to value 'new.value'."_
     - _"Delete the entry with key 'my.test'."_
   - Responses from the LLM are structured as JSON:
     ```json
     {
       "action": "insert",
       "key": "my.test",
       "value": "my.value"
     }
     ```

### 2. **Backend Key-Value Store**
   - **Fields**:
     - `Key`
     - `Value`
     - `Created Datetime`
     - `Updated Datetime`
   - Tracks changes for auditing.

### 3. **User Interface**
   - Built using **Gradio** for simplicity and accessibility.

---

## Usage
1. Start the application using one of the commands from the **Run the Application** section.
2. Access the UI at `http://127.0.0.1:7860`.
3. Interact with the AI agent using natural language to perform backend operations.

---

## Testing
1. **Run Tests**:
   ```bash
   python tests/test.py
   ```
2. **Scenarios Covered**:
   - Valid requests for insert, update, and delete operations.
   - Invalid or ambiguous requests with graceful error handling.
3. Review test results in the `test_results.log` file.

---

## Limitations & Future Enhancements
1. **Limitations**:
   - May require fine-tuning for highly complex queries.
   - Dependency on LLM accuracy for interpreting instructions.

2. **Future Work**:
   - Add support for batch operations.
   - Extend backend system to use a database for persistence.

---

## Author
**Niveditha​ ,Aishwarya​ , Harsha​ ,Koushik **

For any queries or contributions, feel free to reach out!
