import json
import os
from typing import Dict

FILE_PATH = "pokedex.json"

def load_pokedex() -> Dict[int, dict]:
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            raw_data = json.load(file)

            # 🧠 Case 1: If it's a list, convert to dict with numeric keys
            if isinstance(raw_data, list):
                return {i + 1: entry for i, entry in enumerate(raw_data)}

            # 🧠 Case 2: If keys are strings (from JSON), convert to integers
            return {int(k): v for k, v in raw_data.items()}

    return {}

def save_pokedex(data: Dict[int, dict]):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)
