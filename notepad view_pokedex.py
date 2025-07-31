import json

try:
    with open("data/pokedex.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print("✅ Pokédex contents loaded successfully:\n")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        # 🧪 Bonus: Show key types for debugging PATCH/DELETE issues
        print("\n🔍 Key Type Diagnostics:")
        for key in data:
            print(f"Key: {key} | Type: {type(key).__name__} | Name: {data[key].get('name')}")

except Exception as e:
    print("❌ Failed to load pokedex.json:")
    import traceback
    traceback.print_exc()
