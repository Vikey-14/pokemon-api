# core_app.py

import sys
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
import logging

logging.basicConfig(level=logging.DEBUG)

# 📁 Add root path for project-wide module discovery
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ✅ Load .env based on APP_ENV
from dotenv import load_dotenv

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV == "test":
    load_dotenv(".env.test")
elif APP_ENV == "production":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env")

# 🧠 Logging + Middleware
from logger_middleware import LoggingMiddleware
from custom_logger import info_logger, error_logger
from utils.secure_static import SecureStaticFiles
from utils.security_headers import SecurityHeadersMiddleware

# ✅ NEW: use limiter from limiter_utils
from utils.limiter import limiter, _rate_limit_exceeded_handler


from config import settings

# 📦 Routers
from routers import (
    pokemon,
    team,
    trainer,
    upload_csv,
    upload_image,
    upload_misc,
    upload_secure_image,
    gallery,
    upload_csv_validated,
    download
)
from auth.hybrid_auth import router as hybrid_auth_router

# 🔍 Detect test mode
def is_testing_env():
    return os.getenv("TESTING", "0") == "1"

# ✅ Helper: Enable HTTPS redirect in production only
def enable_https_redirect():
    if APP_ENV == "production":
        from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
        core_app.add_middleware(HTTPSRedirectMiddleware)
        print("🔒 HTTPS redirect middleware ENABLED (production)")
    else:
        print("🧪 HTTPS redirect DISABLED (dev/test)")

# 🚀 Initialize FastAPI app
core_app = FastAPI(
    title="Modular Pokémon API",
    description="A FastAPI-powered PokéCenter for trainers worldwide.",
    version="1.0",
    debug=settings.debug,
    docs_url=None if APP_ENV == "production" else "/docs",
    redoc_url=None if APP_ENV == "production" else "/redoc",
    openapi_url=None if APP_ENV == "production" else "/openapi.json"
)

# 🔐 Enable HTTPS only in production
enable_https_redirect()

# 🧠 Rate Limiting
if not is_testing_env():
    core_app.state.limiter = limiter
    core_app.add_middleware(SlowAPIMiddleware)
    core_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    info_logger.info("✅ Rate limiter middleware enabled.")
else:
    info_logger.info("🧪 Testing mode: Rate limiter middleware disabled.")

# 📜 Logging Middleware
try:
    core_app.add_middleware(LoggingMiddleware)
    info_logger.info("✅ Logging middleware enabled.")
except Exception as e:
    error_logger.error(f"❌ Failed to enable logging middleware: {str(e)}")

# 🛡️ Security Headers
try:
    core_app.add_middleware(SecurityHeadersMiddleware)
    info_logger.info("✅ SecurityHeaders middleware enabled.")
except Exception as e:
    error_logger.error(f"❌ Failed to enable security headers: {str(e)}")

# 🔓 CORS (for local + web frontend)
core_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 📂 Serve static files
core_app.mount("/uploads", SecureStaticFiles(directory="uploads"), name="secure-uploads")

# 🔗 Routers
core_app.include_router(hybrid_auth_router)
core_app.include_router(pokemon.router)
core_app.include_router(team.router)
core_app.include_router(trainer.router)
core_app.include_router(upload_csv.router)
core_app.include_router(upload_csv_validated.router)
core_app.include_router(upload_image.router)
core_app.include_router(upload_secure_image.router)
core_app.include_router(upload_misc.router)
core_app.include_router(gallery.router)
core_app.include_router(download.router)
