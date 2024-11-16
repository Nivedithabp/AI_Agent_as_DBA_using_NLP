from intent_classifier import classify_intent

test_inputs = [
    "Insert a record with key 'user_age' and value '25'.",
    "Update the key 'user_name' to 'AdminUser'.",
    "Delete the key 'user_age'.",
    "Tell me a joke."
]

for input_text in test_inputs:
    intent = classify_intent(input_text)
    print(f"Input: {input_text} | Intent: {intent}")
