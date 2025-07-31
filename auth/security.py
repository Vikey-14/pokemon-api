# auth/security.py

from fastapi import APIRouter, HTTPException, status, Form, Depends, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
from utils.limiter import limiter
from users.fake_db import default_user  # ✅ Centralized dummy trainer
import os

router = APIRouter(tags=["Trainer View"])

# ✅ Secret key setup with fallback
SECRET_KEY = os.getenv("SECRET_KEY", "pikachu-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ✅ Pulling credentials and role from shared source
VALID_USERNAME = default_user["username"]
VALID_PASSWORD = default_user["password"]
VALID_ROLE = default_user.get("role", "trainer")  # Defaults to 'trainer'

# ✅ Login route to issue JWT token
@router.post(
    "/login",
    summary="Trainer Login",
    description="Login using trainer credentials and receive a secure token."
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username != VALID_USERNAME or password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # ✅ Include role in the payload
    payload = {
        "sub": username,
        "role": VALID_ROLE,  # 🔑 This line fixes the issue
        "exp": expiry
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return JSONResponse(content={
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
    })

# ✅ OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ✅ Token verification logic
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role", "trainer")  # Default to 'trainer' if not present

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token: No subject"
            )

        return {
            "username": username,
            "role": role
        }

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

