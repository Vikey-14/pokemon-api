# config.py
from pydantic_settings import BaseSettings  

class Settings(BaseSettings):
    # your environment vars here
    app_name: str = "Pokémon API"
    debug: bool = True

settings = Settings()
