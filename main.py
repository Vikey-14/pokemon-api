import sys
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

# ✅ Logging Middleware + Custom Logger
from logger_middleware import LoggingMiddleware
from custom_logger import info_logger, error_logger

# 🔗 Modular Routers
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

# 🔐 Auth Router
from auth.hybrid_auth import router as hybrid_auth_router

# 🛠 Ensure app root is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🚀 Initialize app
app = FastAPI(
    title="Modular Pokémon API",
    description="A FastAPI-powered Pokédex built with modular routers, file handling, security, and trainer tools.",
    version="1.0"
)

# 🧠 Attach global request logging middleware (with fallback safety)
try:
    app.add_middleware(LoggingMiddleware)
    info_logger.info("✅ Logging middleware enabled successfully.")
except Exception as e:
    error_logger.error(f"❌ Failed to attach logging middleware: {str(e)}")

# 🌍 CORS config (⚠️ Secure in production)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧩 Register Routers
app.include_router(pokemon.router)
app.include_router(team.router)
app.include_router(trainer.router)
app.include_router(hybrid_auth_router)

app.include_router(upload_csv.router)
app.include_router(upload_csv_validated.router)
app.include_router(upload_image.router)
app.include_router(upload_secure_image.router)
app.include_router(upload_misc.router)

app.include_router(gallery.router)
app.include_router(download.router)

# 🖼 Serve static uploads (for Swagger preview)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 🪵 Background event log for Pokémon addition
def log_pokemon_addition(trainer: str, pokemon_name: str, pokemon_id: int):
    file_path = os.path.abspath("poke_logs.txt")
    print(f"📂 Writing log file to: {file_path}")  # Optional debug print
    with open(file_path, "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] Trainer {trainer} added {pokemon_name} (ID: {pokemon_id}) to the Pokédex.\n")

# ❌ Global error logging
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_logger.error(f"{request.method} {request.url.path} → {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
