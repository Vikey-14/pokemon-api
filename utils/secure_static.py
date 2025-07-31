from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from fastapi import HTTPException, status
import os

# 🚫 Forbidden extensions
BLOCKED_EXTENSIONS = {".py", ".env", ".log", ".sh", ".exe", ".bat"}

# ✅ Allowed subfolders only (adjust as needed)
ALLOWED_PATHS = {"uploads/images", "uploads/csv", "uploads/gallery"}

class SecureStaticFiles(StaticFiles):
    async def get_response(self, path: str, request: Request):
        full_path = os.path.abspath(os.path.join(self.directory, path))

        # 🔐 Block if extension is forbidden
        ext = os.path.splitext(full_path)[1].lower()
        if ext in BLOCKED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this file type is forbidden.")

        # 🔐 Block if trying to access outside allowed folders
        if not any(full_path.startswith(os.path.abspath(folder)) for folder in ALLOWED_PATHS):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access outside allowed folders is forbidden.")

        return await super().get_response(path, request)
