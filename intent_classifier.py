from transformers import pipeline

# Using a zero-shot classifier for better performance
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_intent(text):
    labels = ["insert", "update", "delete", "irrelevant"]
    result = classifier(text, candidate_labels=labels)
    return result["labels"][0]  # Top predicted label
