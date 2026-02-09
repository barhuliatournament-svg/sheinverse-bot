import json
import os

FILE = "stock_cache.json"

def load_stock():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save_stock(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
