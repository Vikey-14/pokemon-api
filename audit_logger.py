import os
from datetime import datetime
from custom_logger import info_logger

# 🧪 Flag to detect if in test mode
TESTING = os.getenv("TESTING", "0") == "1"

def log_pokemon_addition(trainer: str, pokemon_name: str, pokemon_id: int):
    """
    Logs when a trainer adds a Pokémon to the Pokédex.
    """
    log_message = f"Trainer {trainer} added {pokemon_name} (ID: {pokemon_id}) to the Pokédex."

    # ✅ Print emoji logs only if not testing
    if not TESTING:
        print(f"📂 Logging: {log_message}")
    else:
        print(f"Logging: {log_message}")  # Cleaner test output

    # ✅ Save to file using info logger
    info_logger.info(log_message)
