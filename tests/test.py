import unittest
from datetime import datetime
from backend_store import KeyValueStore  # Assume you have a module for the key-value store
from llm_agent import process_request  # Assume you have a module for the LLM agent


class TestBackendOperations(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()

    def test_insert_operation(self):
        response = process_request("Insert key 'test.key' with value 'test.value'.")
        self.assertEqual(response['action'], 'insert')
        self.assertEqual(response['key'], 'test.key')
        self.assertEqual(response['value'], 'test.value')

        # Perform insert
        self.store.insert(response['key'], response['value'])
        entry = self.store.get(response['key'])
        self.assertEqual(entry['value'], 'test.value')

    def test_update_operation(self):
        self.store.insert('test.key', 'initial.value')
        response = process_request("Update key 'test.key' to value 'updated.value'.")
        self.assertEqual(response['action'], 'update')
        self.assertEqual(response['key'], 'test.key')
        self.assertEqual(response['value'], 'updated.value')

        # Perform update
        self.store.update(response['key'], response['value'])
        entry = self.store.get(response['key'])
        self.assertEqual(entry['value'], 'updated.value')

    def test_delete_operation(self):
        self.store.insert('test.key', 'test.value')
        response = process_request("Delete the entry with key 'test.key'.")
        self.assertEqual(response['action'], 'delete')
        self.assertEqual(response['key'], 'test.key')

        # Perform delete
        self.store.delete(response['key'])
        entry = self.store.get(response['key'])
        self.assertIsNone(entry)

    def test_invalid_request(self):
        response = process_request("Show me the key-value pairs.")
        self.assertEqual(response['action'], 'error')
        self.assertIn('Invalid request', response['message'])


class TestKeyValueStore(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()

    def test_insert(self):
        key = 'test.key'
        value = 'test.value'
        self.store.insert(key, value)
        entry = self.store.get(key)
        self.assertEqual(entry['value'], value)
        self.assertIsInstance(entry['created_at'], datetime)

    def test_update(self):
        key = 'test.key'
        value = 'test.value'
        updated_value = 'updated.value'
        self.store.insert(key, value)
        self.store.update(key, updated_value)
        entry = self.store.get(key)
        self.assertEqual(entry['value'], updated_value)
        self.assertNotEqual(entry['created_at'], entry['updated_at'])

    def test_delete(self):
        key = 'test.key'
        self.store.insert(key, 'test.value')
        self.store.delete(key)
        entry = self.store.get(key)
        self.assertIsNone(entry)


if __name__ == "__main__":
    unittest.main()
