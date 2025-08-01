# 🚀 Ensure root path is discoverable for imports (like utils.file_handler)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🧪 FastAPI App Entry Point (Trigger auto-deploy test ✅)

from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from core_app import core_app as app  # ✅ Pulls the real app from core
from custom_logger import error_logger
from datetime import datetime

# ✅ Import limit_safe for future use (if needed)
from utils.limiter_utils import limit_safe

# ✅ Optional Background Logger
def log_pokemon_addition(trainer: str, pokemon_name: str, pokemon_id: int):
    file_path = os.path.abspath("poke_logs.txt")
    print(f"📂 Writing log file to: {file_path}")
    with open(file_path, "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] Trainer {trainer} added {pokemon_name} (ID: {pokemon_id}) to the Pokédex.\n")

# ✅ HTML Welcome Page with HEAD support to silence 405
@app.get("/", response_class=HTMLResponse)
@app.head("/", include_in_schema=False)  # 🧼 Added to prevent Render 405 logs
def home():
    return """
    <html lang="en">
    ...
    <a href='/docs'>Enter PokéCenter API</a>
    </body>
    </html>
    """

# ✅ Test Security Headers
@app.get("/test/security")
def check_security_headers():
    return {"message": "Check the response headers in Swagger or Postman"}

# ✅ Global Error Handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_logger.error(f"{request.method} {request.url.path} → {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    error_logger.warning(f"🚫 Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Too Many Requests. Slow down, trainer! 🐢" }
    )
