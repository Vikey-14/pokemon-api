# utils/limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Grab current environment mode
APP_ENV = os.getenv("APP_ENV", "development")
TESTING = os.getenv("TESTING", "0") == "1"

# ✅ Custom key function that works even in tests without real client IP
def safe_key_func(request: Request):
    try:
        # Handle missing client info in tests or mocks
        return request.client.host or "test-client"
    except Exception:
        return "test-client"

# ✅ Create limiter with correct key_func depending on environment
if TESTING or APP_ENV == "test":
    limiter = Limiter(key_func=safe_key_func)  # ✅ Safe even in pytest mode
else:
    limiter = Limiter(key_func=get_remote_address)

# ✅ Custom error handler for rate limiting
def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "❌ You are being rate limited. Please slow down."}
    )
