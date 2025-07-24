# dependencies/pokedex_provider.py

from file_handler import load_pokedex, save_pokedex
from typing import Dict

def get_pokedex_data() -> Dict[int, dict]:
    pokedex = load_pokedex()
    return pokedex
