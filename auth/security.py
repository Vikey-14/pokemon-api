from fastapi import APIRouter, HTTPException, status, Form, Request, Depends
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError  # ✅ For token encoding/decoding
from jose.exceptions import ExpiredSignatureError  # ✅ Specific exception for expired tokens
from fastapi.security import OAuth2PasswordBearer
import os

router = APIRouter()

# ✅ Secret key setup with fallback
SECRET_KEY = os.getenv("SECRET_KEY", "pikachu-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ✅ Dummy trainer login credentials (replace with DB call in real app)
VALID_USERNAME = "ash"
VALID_PASSWORD = "pikachu123"


# ✅ Login route to issue JWT token
@router.post(
    "/login",
    tags=["Trainer View"],
    summary="Trainer Login",
    description="Login using trainer credentials and receive a secure token."
)
async def login(username: str = Form(...), password: str = Form(...)):
    if username != VALID_USERNAME or password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # ✅ Generate JWT token with expiry
    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "exp": expiry
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return JSONResponse(content={
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
    })


# ✅ OAuth2 scheme for protecting routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ✅ Token verification logic (Upgraded!)
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # ✅ Validate token signature + expiry
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token: No subject"
            )
        return username

    except ExpiredSignatureError:  # ✅ Specific error for expired tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except JWTError:  # ✅ General catch for malformed/invalid tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
