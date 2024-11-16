from datetime import datetime

class KeyValueStore:
    def __init__(self):
        self.store = {}

    def insert(self, key, value):
        if key in self.store:
            return "Key already exists."
        self.store[key] = {"value": value, "created": datetime.now(), "updated": datetime.now()}
        return f"Inserted key '{key}' with value '{value}'."

    def update(self, key, value):
        if key not in self.store:
            return "Key does not exist."
        self.store[key]["value"] = value
        self.store[key]["updated"] = datetime.now()
        return f"Updated key '{key}' with value '{value}'."

    def delete(self, key):
        if key not in self.store:
            return "Key does not exist."
        del self.store[key]
        return f"Deleted key '{key}'."
