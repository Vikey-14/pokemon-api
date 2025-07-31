# 🚀 Ensure root path is discoverable for imports (like utils.file_handler)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# main.py — boots up the real app from core
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
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to the PokéCenter</title>
        <link rel="icon" href="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" type="image/png" />
        <style>
            body {
                margin: 0;
                padding: 0;
                height: 100vh;
                background: linear-gradient(-45deg, #ffccd5, #fff0f5, #c1c8e4, #fbeaff);
                background-size: 400% 400%;
                animation: gradientFlow 15s ease infinite;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            @keyframes gradientFlow {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            img {
                width: 120px;
                margin-bottom: 20px;
                animation: bounce 1.5s infinite;
            }
            h1 {
                color: #cc0000;
                font-size: 2.5rem;
            }
            p {
                font-size: 1.2rem;
                color: #333;
                max-width: 500px;
            }
            a {
                display: inline-block;
                margin-top: 25px;
                padding: 12px 25px;
                background-color: #cc0000;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            a:hover {
                background-color: #990000;
            }
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
        </style>
    </head>
    <body>
        <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="PokéBall Logo" />
        <h1>Welcome to the PokéCenter!</h1>
        <p>Nurse Joy is ready to assist you. Explore the trainer tools and Pokédex via our API below.</p>
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
        content={"detail": "Too Many Requests. Slow down, trainer! 🐢"}
    )
