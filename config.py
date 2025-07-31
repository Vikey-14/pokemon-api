import os
import sys
from pydantic import Field
from typing import Optional  # ✅ Needed for Pydantic v2 defaults
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# --------------------------------------------------------------------------------
# ✅ 1. Auto-enable TESTING=1 if pytest is detected
# --------------------------------------------------------------------------------
if "pytest" in sys.modules:
    os.environ["TESTING"] = "1"

# --------------------------------------------------------------------------------
# ✅ 2. Determine which .env file to load
# --------------------------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "development")

if os.getenv("TESTING", "0") == "1" or APP_ENV == "test":
    dotenv_path = ".env.test"
elif APP_ENV == "production":
    dotenv_path = ".env"  # Docker copies `.env.prod` to `.env` during build
else:
    dotenv_path = ".env.local"

# ✅ Load environment variables from the selected file
load_dotenv(dotenv_path=dotenv_path)

# --------------------------------------------------------------------------------
# ✅ 3. Define settings using Pydantic for validation and structure
# --------------------------------------------------------------------------------
class Settings(BaseSettings):
    # 🌐 General App Info
    app_name: str = "Pokémon API"
    debug: bool = True

    # 🔐 JWT Auth
    SECRET_KEY: str = Field(default="test-secret-key", validate_default=True) # ✅ FIXED: Pydantic v2 requires Optional + default
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRY_MINUTES: int = 60

    # 📁 File Uploads
    UPLOAD_DIR: str = "uploads"
    ALLOWED_IMAGE_TYPES: str = "image/"

    # 🧪 Environment Flags
    TESTING: bool = os.getenv("TESTING", "0") == "1"
    APP_ENV: str = APP_ENV

    # 🌐 HTTPS Redirect Toggle (used in middleware)
    FORCE_HTTPS: bool = os.getenv("FORCE_HTTPS", "0") == "1"

    class Config:
        env_file = dotenv_path
        env_file_encoding = "utf-8"

# ✅ Global instance used throughout the project
settings = Settings()

# 🧪 Optional log for verification
print(f"✅ CONFIG LOADED — ENV: {settings.APP_ENV} | TESTING: {settings.TESTING} | HTTPS: {settings.FORCE_HTTPS}")
