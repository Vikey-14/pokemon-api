import json
import traceback

print("🔍 Opening Pokédex file at: data/pokedex.json")

try:
    with open("data/pokedex.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print("✅ Pokédex contents loaded successfully:\n")
        print(json.dumps(data, indent=4))
except Exception as e:
    print("❌ Failed to load pokedex.json")
    print("🔥 Error:", str(e))
    traceback.print_exc()
