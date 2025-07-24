from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# ✅ Load .env before accessing variables
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Pokémon API"
    debug: bool = True
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRY_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
