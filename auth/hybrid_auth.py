from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from config import settings
from jose import jwt, JWTError, ExpiredSignatureError
from custom_logger import info_logger, error_logger  # ✅ Import both loggers
import uuid

# 🔐 Secret key and algorithm for JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

# 🧠 In-memory store for refresh tokens with expiry
refresh_token_store = {}

# 🧍 Dummy user (replace with DB logic later)
fake_user = {
    "username": "ashketchum",
    "password": "pikapika",
    "role": "trainer"
}

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🧠 Pydantic models
class LoginInput(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# 🔑 Token generator
def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🛡️ Extract bearer token
security = HTTPBearer()

# 🟢 Login Route
@router.post("/login", response_model=TokenPair)
def login_user(login: LoginInput):
    if login.username != fake_user["username"] or login.password != fake_user["password"]:
        error_logger.error(f"❌ Login failed for user '{login.username}' – Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token(
        {"sub": fake_user["username"], "role": fake_user["role"]},
        expires_delta=timedelta(hours=1)
    )

    refresh_token = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(days=7)

    refresh_token_store[fake_user["username"]] = {
        "token": refresh_token,
        "expires_at": expiry
    }

    info_logger.info(f"🔐 '{login.username}' logged in. Access + refresh tokens issued.")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

# 🔁 Refresh Token Route
@router.post("/refresh-token", response_model=TokenPair)
def rotate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    incoming_refresh_token = credentials.credentials

    for username, token_info in refresh_token_store.items():
        stored_token = token_info["token"]
        expiry_time = token_info["expires_at"]

        if stored_token == incoming_refresh_token:
            if datetime.utcnow() > expiry_time:
                error_logger.error(f"⏳ Refresh token expired for '{username}'")
                raise HTTPException(status_code=401, detail="Refresh token expired")

            new_refresh_token = str(uuid.uuid4())
            new_expiry = datetime.utcnow() + timedelta(days=7)
            refresh_token_store[username] = {
                "token": new_refresh_token,
                "expires_at": new_expiry
            }

            new_access_token = create_token(
                {"sub": username, "role": fake_user["role"]},
                expires_delta=timedelta(hours=1)
            )

            info_logger.info(f"🔁 '{username}' rotated refresh token successfully.")
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            }

    error_logger.error(f"❌ Invalid refresh token attempt: {incoming_refresh_token}")
    raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# ✅ Extract current user from access token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            error_logger.error("❌ Access token missing username or role")
            raise HTTPException(status_code=401, detail="Invalid access token")

        info_logger.info(f"✅ Access token valid for '{username}'.")
        return {"username": username, "role": role}

    except ExpiredSignatureError:
        error_logger.error("⛔ Access token expired.")
        raise HTTPException(status_code=401, detail="Access token expired")
    except JWTError:
        error_logger.error("⛔ Access token decoding failed.")
        raise HTTPException(status_code=401, detail="Invalid access token")

# 🔐 Role-based protection
def role_required(required_role: str):
    def role_dependency(user: dict = Depends(get_current_user)):
        if user["role"] != required_role:
            error_logger.error(f"🚫 Access denied – '{user['username']}' attempted '{required_role}' access")
            raise HTTPException(status_code=403, detail="Forbidden: You are not authorized")
        return user
    return role_dependency

# 🔍 Whoami route
@router.get("/whoami")
def whoami(user: dict = Depends(get_current_user)):
    return {"message": f"You are {user['username']} with role {user['role']}"}
