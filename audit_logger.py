from datetime import datetime
from custom_logger import info_logger  # ✅ Using shared logger

def log_pokemon_addition(trainer: str, pokemon_name: str, pokemon_id: int):
    log_message = f"Trainer {trainer} added {pokemon_name} (ID: {pokemon_id}) to the Pokédex."
    
    # Optional print for confirmation in console
    print(f"📂 Logging: {log_message}")

    # ✅ Log to file using consistent logging format
    info_logger.info(log_message)
