# routers/download.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from auth.hybrid_auth import get_current_user
from utils.limiter_utils import limit_safe
from custom_logger import info_logger, error_logger
from pathlib import Path

router = APIRouter(tags=["Trainer View"])

# 📁 Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
IMAGE_DIR = UPLOAD_DIR / "images"
LOG_DIR = BASE_DIR / "logs"

#️⃣ ✅ STATIC ROUTE FIRST: Download battle log
@router.get("/download/log", summary="Download battle log")
@limit_safe("3/minute")
async def download_battle_log(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    file_path = LOG_DIR / "battle_log.txt"

    if not file_path.exists():
        error_logger.error(f"❌ Battle log not found: {file_path}")
        raise HTTPException(status_code=404, detail="Battle log not found.")

    info_logger.info(f"📥 Trainer '{current_user['username']}' downloaded 'battle_log.txt'")
    return FileResponse(path=file_path, filename="battle_log.txt", media_type="text/plain")

#️⃣ ✅ STATIC ROUTE SECOND: Download image by name
@router.get("/download/image/{filename}", summary="Download image by filename")
@limit_safe("10/minute")
async def download_image(
    request: Request,
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    file_path = IMAGE_DIR / filename

    if not file_path.exists():
        error_logger.error(f"❌ Image not found: {file_path}")
        raise HTTPException(status_code=404, detail="Image not found.")

    info_logger.info(f"🖼️ Image '{filename}' downloaded by '{current_user['username']}'")
    return FileResponse(path=file_path, filename=filename, media_type="image/png")

#️⃣ ✅ DYNAMIC ROUTE LAST: Download any uploaded CSV/log by filename
@router.get("/download/{filename}", summary="Download uploaded CSV or log file")
@limit_safe("5/minute")
async def download_uploaded_file(
    request: Request,
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        error_logger.error(f"❌ File not found: {file_path}")
        raise HTTPException(status_code=404, detail="Battle log not found.")

    info_logger.info(f"📥 File '{filename}' downloaded by '{current_user['username']}'")
    return FileResponse(path=file_path, filename=filename)