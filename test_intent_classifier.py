from intent_classifier import classify_intent

def test_classification():
    inputs = [
        "Insert a record with key 'user_age' and value '25'.",
        "Update the key 'user_age' to '30'.",
        "Delete the key 'user_age'.",
        "Tell me a joke."
    ]

    for input_text in inputs:
        print(f"Input: {input_text} | Intent: {classify_intent(input_text)}")

test_classification()
