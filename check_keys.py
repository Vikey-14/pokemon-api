from utils.file_handler import load_pokedex

pokedex = load_pokedex()
print("📘 Keys in pokedex.json:", list(pokedex.keys()))
