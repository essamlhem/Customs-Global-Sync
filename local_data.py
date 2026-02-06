import json
import os

def save_to_local(data):
    with open("data_backup.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_from_local():
    if os.path.exists("data_backup.json"):
        with open("data_backup.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None
