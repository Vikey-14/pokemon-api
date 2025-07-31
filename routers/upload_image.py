from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from typing import List
from utils.limiter_utils import limit_safe  # ✅ Safe limiter for test bypass
from auth.hybrid_auth import get_current_user
from utils.file_utils import validate_file_upload, save_file 
from custom_logger import info_logger, error_logger
import os

router = APIRouter(tags=["Admin Actions"])

# 📁 Directory to store uploaded images
UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#️⃣ Single Image Upload
@router.post(
    "/upload/image",
    summary="Upload a single image",
    description="Saves one image to disk. Requires authentication."
)
@limit_safe("5/minute")  # ✅ Safe limiter
async def upload_image(
    request: Request, 
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        validate_file_upload(file)
        filename = save_file(file, UPLOAD_DIR)
        info_logger.info(f"🖼️ Image '{file.filename}' uploaded by Trainer '{user['username']}' → saved as '{filename}'.")
        return JSONResponse(status_code=201, content={
            "message": "Image uploaded!",
            "filename": filename
        })

    except HTTPException:
        raise

    except Exception as e:
        error_logger.error(f"💥 Failed to save image '{file.filename}' by '{user.get('username', 'unknown')}': {str(e)}")
        raise HTTPException(status_code=500, detail="Image upload failed due to a server error.")

#️⃣ Multiple Image Uploads
@router.post(
    "/upload/images",
    summary="Upload multiple images",
    description="Saves multiple images. Requires authentication."
)
@limit_safe("3/minute")  # ✅ Safe limiter
async def upload_multiple_images(
    request: Request,
    files: List[UploadFile] = File(...),
    user=Depends(get_current_user)
):
    saved_files = []

    for file in files:
        try:
            validate_file_upload(file)
            filename = save_file(file, UPLOAD_DIR)
            saved_files.append(filename)
            info_logger.info(f"🖼️ Image '{file.filename}' uploaded by '{user['username']}' → saved as '{filename}'")

        except HTTPException as http_ex:
            error_logger.warning(f"⚠️ Validation failed for '{file.filename}' by '{user['username']}': {http_ex.detail}")
            raise http_ex

        except Exception as e:
            error_logger.error(f"💥 Error saving image '{file.filename}' by '{user['username']}': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save image: {file.filename}")

    return JSONResponse(status_code=201, content={
        "message": f"{len(saved_files)} image(s) uploaded!",
        "filenames": saved_files
    })
