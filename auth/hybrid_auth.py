from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from config import settings
from jose import jwt, JWTError, ExpiredSignatureError
from custom_logger import info_logger, error_logger
from utils.limiter_utils import limit_safe
from typing import Any
import uuid
import os

print("[AUTH_BC] AUTH_MODULE_IMPORTED file=auth/hybrid_auth.py", flush=True)

def _clip(v: Any, limit: int = 180) -> str:
    try:
        s = repr(v)
    except Exception:
        s = f"<unrepr:{type(v).__name__}>"
    return s if len(s) <= limit else s[:limit] + "…"


def _auth_bc(event: str, **fields) -> None:
    """
    Render-visible breadcrumb logger.
    Uses print(..., flush=True) so breadcrumbs appear in Render Logs.
    """
    try:
        parts = " ".join(f"{k}={_clip(v)}" for k, v in fields.items())
        print(f"[AUTH_BC] {event}" + (f" {parts}" if parts else ""), flush=True)
    except Exception as e:
        print(f"[AUTH_BC] {event} breadcrumb_error={type(e).__name__}:{e}", flush=True)

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
        _auth_bc(
            "AUTH_CREATE_TOKEN_ENTER",
            data_keys=sorted(list(data.keys())),
            sub=data.get("sub"),
            role=data.get("role"),
            expires_delta_seconds=int(expires_delta.total_seconds()),
            algorithm=ALGORITHM,
            testing=TESTING,
            app_env=settings.APP_ENV,
            secret_present=bool(SECRET_KEY),
            secret_len=len(SECRET_KEY or ""),
            secret_type=type(SECRET_KEY).__name__,
        )

        payload = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        issued_at = datetime.now(timezone.utc)

        payload.update({
            "exp": expire,
            "iat": issued_at,
            "jti": str(uuid.uuid4())
        })

        _auth_bc(
            "AUTH_CREATE_TOKEN_PAYLOAD_READY",
            sub=payload.get("sub"),
            role=payload.get("role"),
            exp_type=type(payload.get("exp")).__name__,
            iat_type=type(payload.get("iat")).__name__,
            jti_present=bool(payload.get("jti")),
        )

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        _auth_bc(
            "AUTH_CREATE_TOKEN_OK",
            token_len=len(token or ""),
            token_type=type(token).__name__,
        )
        return token

    except JOSEError as e:
        _auth_bc(
            "AUTH_CREATE_TOKEN_JOSE_ERR",
            err_type=type(e).__name__,
            err=str(e),
            algorithm=ALGORITHM,
            secret_present=bool(SECRET_KEY),
            secret_len=len(SECRET_KEY or ""),
        )
        raise HTTPException(status_code=500, detail="JWT creation failed")

    except Exception as e:
        _auth_bc(
            "AUTH_CREATE_TOKEN_ERR",
            err_type=type(e).__name__,
            err=str(e),
            algorithm=ALGORITHM,
            secret_present=bool(SECRET_KEY),
            secret_len=len(SECRET_KEY or ""),
        )
        raise HTTPException(status_code=500, detail="Token creation failed")


# 🔓 Login Route
@router.post("/login")
@limit_safe("5/minute")
async def login_user(request: Request, login: LoginInput):
    _auth_bc(
        "AUTH_LOGIN_ENTER",
        method=request.method,
        path=request.url.path,
        content_type=request.headers.get("content-type"),
        app_env=settings.APP_ENV,
        testing=TESTING,
        algorithm=ALGORITHM,
        secret_present=bool(SECRET_KEY),
        secret_len=len(SECRET_KEY or ""),
        fake_user_count=len(fake_users),
    )

    try:
        _auth_bc(
            "AUTH_LOGIN_BODY_PARSED",
            username=login.username,
            has_password=bool(login.password),
            password_len=len(login.password or ""),
        )

        user = fake_users.get(login.username)
        _auth_bc(
            "AUTH_LOGIN_USER_LOOKUP",
            username=login.username,
            user_found=bool(user),
        )

        if not user:
            _auth_bc("AUTH_LOGIN_INVALID_USER", username=login.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        pwd_ok = user["password"] == login.password
        _auth_bc(
            "AUTH_LOGIN_PASSWORD_CHECK",
            username=login.username,
            pwd_ok=pwd_ok,
        )

        if not pwd_ok:
            _auth_bc("AUTH_LOGIN_INVALID_PASSWORD", username=login.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        _auth_bc(
            "AUTH_LOGIN_CREATE_TOKEN_BEGIN",
            username=login.username,
            role=user.get("role"),
        )

        access_token = create_token(
            {"sub": login.username, "role": user["role"]},
            expires_delta=timedelta(hours=1)
        )

        _auth_bc(
            "AUTH_LOGIN_CREATE_TOKEN_DONE",
            username=login.username,
            access_token_len=len(access_token or ""),
        )

        refresh_token = str(uuid.uuid4())
        _auth_bc(
            "AUTH_LOGIN_REFRESH_STORE_BEGIN",
            username=login.username,
            store_size_before=len(refresh_token_store),
        )

        refresh_token_store[login.username] = {
            "token": refresh_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
        }

        _auth_bc(
            "AUTH_LOGIN_REFRESH_STORE_DONE",
            username=login.username,
            refresh_token_len=len(refresh_token),
            store_size_after=len(refresh_token_store),
        )

        _auth_bc(
            "AUTH_LOGIN_OK",
            username=login.username,
            role=user.get("role"),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except HTTPException as e:
        _auth_bc(
            "AUTH_LOGIN_HTTP_EXC",
            username=getattr(login, "username", None),
            status_code=e.status_code,
            detail=e.detail,
        )
        raise

    except Exception as e:
        _auth_bc(
            "AUTH_LOGIN_ERR",
            username=getattr(login, "username", None),
            err_type=type(e).__name__,
            err=str(e),
        )
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
