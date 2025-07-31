from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from config import settings
from jose import jwt, JWTError, ExpiredSignatureError
from custom_logger import info_logger, error_logger
from utils.limiter_utils import limit_safe
import uuid
import os

# 🔐 JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
TESTING = settings.TESTING

# 🧠 Token Store (in-memory for refresh tokens)
refresh_token_store = {}
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Auth"])

# 👤 Fake users for testing
if TESTING:
    fake_users = {
        "ashketchum": {
            "username": "ashketchum",
            "password": "pikapika",
            "role": "trainer"
        },
        "professoroak": {
            "username": "professoroak",
            "password": "pallet123",
            "role": "admin"
        }
    }
else:
    from users.fake_db import fake_users


# 🧾 Pydantic Schemas
class LoginInput(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# 🛡️ Token Decoder 
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        info_logger.info(f"🧾 Decoding token: {credentials.credentials}")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"username": username, "role": role}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except JWTError as e:
        error_logger.error(f"❌ JWT decode failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


# 🔐 Role Checker
def role_required(required_role: str):
    def wrapper(user: dict = Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return wrapper


# 🔐 Token Generator
def create_token(data: dict, expires_delta: timedelta) -> str:
    from jose.exceptions import JOSEError

    try:
        payload = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        payload.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4())
        })

        info_logger.info(f"🧪 [create_token] Payload: {payload}")
        info_logger.info(f"🔐 SECRET_KEY: {repr(SECRET_KEY)}")
        info_logger.info(f"🧾 Algorithm: {ALGORITHM}")

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        info_logger.info("✅ JWT Created")
        return token

    except JOSEError as e:
        error_logger.error(f"❌ JOSEError: {str(e)}")
        raise HTTPException(status_code=500, detail="JWT creation failed")
    except Exception as e:
        error_logger.exception(f"❌ Unknown error during JWT creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Token creation failed")


# 🔓 Login Route
@router.post("/login")
@limit_safe("5/minute")
async def login_user(request: Request, login: LoginInput):
    info_logger.info("🟢 /auth/login HIT")

    try:
        info_logger.info(f"👥 Users: {fake_users}")
        user = fake_users.get(login.username)
        if not user or user["password"] != login.password:
            error_logger.warning(f"🚫 Login failed for: {login.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_token(
            {"sub": login.username, "role": user["role"]},
            expires_delta=timedelta(hours=1)
        )

        refresh_token = str(uuid.uuid4())
        refresh_token_store[login.username] = {
            "token": refresh_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
        }

        info_logger.info(f"✅ Login successful for {login.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise  # ✅ Preserve real status codes
    except Exception as e:
        error_logger.exception(f"❌ Crash in login_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Login crash")


# 🔁 Refresh Token Route
@router.post("/refresh-token")
@limit_safe("10/minute")
async def rotate_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        incoming = credentials.credentials
        info_logger.info(f"🔄 Refresh attempt with token: {incoming}")

        # 🔍 Search all users for a matching refresh token
        for username, token_info in refresh_token_store.items():
            if token_info["token"] == incoming:
                # ⏳ Check expiry
                if datetime.now(timezone.utc) > token_info["expires_at"]:
                    raise HTTPException(status_code=401, detail="Refresh token expired")

                # 🔍 Get user info
                user = fake_users.get(username)
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")

                # 🔁 Rotate token
                new_refresh_token = str(uuid.uuid4())
                refresh_token_store[username] = {
                    "token": new_refresh_token,
                    "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
                }

                new_access_token = create_token(
                    {"sub": username, "role": user["role"]},
                    expires_delta=timedelta(hours=1)
                )

                info_logger.info(f"✅ Refresh success for {username}")
                return {
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                    "token_type": "bearer"
                }

        # 🚫 If no token matched after full search
        info_logger.warning("🚫 Reused or invalid refresh token detected!")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    except HTTPException as http_exc:
        raise http_exc  # Let FastAPI return the correct status
    except Exception as e:
        error_logger.exception(f"❌ Crash in rotate_token: {str(e)}")
        raise HTTPException(status_code=500, detail="Refresh crash")


# 👤 Whoami Route (CLEAN & YELLOW-FREE)
@router.get("/whoami")
@limit_safe("20/minute")
async def whoami(request: Request, user: dict = Depends(get_current_user)):
    return {"message": f"You are {user['username']} with role {user['role']}"}
