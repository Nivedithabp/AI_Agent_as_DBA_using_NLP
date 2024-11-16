from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_intent(user_input):
    print(f"[DEBUG] Inside classify_intent with input: {user_input}")
    if "insert" in user_input.lower():
        return "insert"
    elif "update" in user_input.lower():
        return "update"
    elif "delete" in user_input.lower():
        return "delete"
    else:
        return "irrelevant"
