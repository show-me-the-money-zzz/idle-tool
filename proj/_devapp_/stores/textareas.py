import os
import json

STORE_FILE = "textareas.json"
TextAreas = {}

def AddItem_TextArea(key, data):
    TextAreas[key] = data
    print(f"store.AddItem_TextArea({key}, {data})")

def GetItem_TextArea(key):
    return TextAreas.get(key)

def DeleteItem_TextArea(key):
    TextAreas.pop(key, None)

def Save_TextAreas():
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(TextAreas, f, indent=2, ensure_ascii=False)

def Load_TextAreas():
    global TextAreas
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            TextAreas = json.load(f)
