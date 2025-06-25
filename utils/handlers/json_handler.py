import json
import os

class JsonHandler:
    @staticmethod
    def load(path):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def update_key(path, key, value):
        data = JsonHandler.load(path)
        data[key] = value
        with open(path, "r+", encoding="utf-8") as f:
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.truncate()

    @staticmethod
    def get_key(path, key, default=None):
        data = JsonHandler.load(path)
        return data.get(key, default)
