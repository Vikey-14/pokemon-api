from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime
from jose import jwt, JWTError
import time
import os

# ⚙️ Logging setup
LOG_DIR = "logs"
LOG_FILE = "middleware_logs.txt"
os.makedirs(LOG_DIR, exist_ok=True)

# 🔐 JWT Setup (same as your app)
SECRET_KEY = "pikachu-secret-key"  # Use your actual key
ALGORITHM = "HS256"

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # ⏱️ Main try block to catch errors
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            response = None

        end_time = time.time()
        duration = round(end_time - start_time, 4)

        # 🌐 Basic request info
        method = request.method
        url = request.url.path
        ip = request.client.host
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 🔐 Extract username from token (if present)
        auth_header = request.headers.get("Authorization")
        username = "Unknown"

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub", "Unknown")
            except JWTError:
                username = "InvalidToken"

        # 📝 Log format
        log_entry = (
            f"[{timestamp}] {method} {url} | 👤 {username} | 📍 {ip} | "
            f"Status: {status_code} | ⏱️ {duration}s\n"
        )

        # 💾 Save log to file with utf-8 to avoid UnicodeEncodeError
        log_path = os.path.join(LOG_DIR, LOG_FILE)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        # 🛑 If error, return fallback response
        return response if response else PlainTextResponse("Internal Server Error", status_code=500)
