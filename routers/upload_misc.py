from fastapi import APIRouter, UploadFile, File, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse
from auth.security import verify_token
from custom_logger import info_logger, error_logger
from utils.file_utils import validate_generic_file
from utils.limiter_utils import limit_safe  
from datetime import datetime
import os

router = APIRouter(tags=["Admin Actions"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


#️⃣ Securely save any file to disk
@router.post("/upload/save", summary="Save file to disk safely")
@limit_safe("3/minute")  # ✅ Bypassed during tests
async def save_uploaded_file(
    request: Request, 
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)
):
    try:
        validate_generic_file(file)

        original_name = file.filename
        file_path = os.path.join(UPLOAD_DIR, original_name)

        if os.path.exists(file_path):
            name_part, ext = os.path.splitext(original_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{name_part}_{timestamp}{ext}"
            file_path = os.path.join(UPLOAD_DIR, new_filename)
        else:
            new_filename = original_name

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        info_logger.info(f"💾 File '{original_name}' saved by '{current_user}' as '{new_filename}'")

        return JSONResponse(content={
            "message": f"✅ File saved by {current_user}!",
            "original_name": original_name,
            "stored_as": new_filename,
            "path": file_path
        })

    except HTTPException:
        raise

    except Exception as e:
        error_logger.error(f"❌ Server error saving file '{file.filename}' by '{current_user}': {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed due to a server error.")


#️⃣ Securely preview text or image files
@router.post("/upload/preview", summary="Read file without saving")
@limit_safe("5/minute")  # ✅ Bypassed during tests
async def preview_uploaded_file(
    request: Request, 
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)
):
    try:
        validate_generic_file(file)
        content = await file.read()

        if file.content_type in ["text/plain", "text/csv", "application/json"]:
            try:
                decoded = content.decode("utf-8")
                preview = decoded[:300]
                lines = preview.splitlines()[:10]

                info_logger.info(f"👁️ Previewed text file '{file.filename}' by '{current_user}'")

                return {
                    "filename": file.filename,
                    "uploaded_by": current_user,
                    "content_type": file.content_type,
                    "preview": lines
                }

            except UnicodeDecodeError:
                error_logger.warning(f"⚠️ Cannot decode '{file.filename}' uploaded by '{current_user}'")
                return {
                    "filename": file.filename,
                    "error": "❌ Failed to decode file. Not valid UTF-8 text."
                }

        elif file.content_type.startswith("image/"):
            info_logger.info(f"🖼️ Image '{file.filename}' uploaded by '{current_user}' (preview skipped)")
            return {
                "filename": file.filename,
                "uploaded_by": current_user,
                "message": "🖼️ Image uploaded. No preview available."
            }

        error_logger.warning(f"⛔ Unsupported preview type for '{file.filename}' by '{current_user}'")
        return {
            "filename": file.filename,
            "uploaded_by": current_user,
            "message": "❌ Unsupported file type for preview."
        }

    except HTTPException:
        raise

    except Exception as e:
        error_logger.error(f"❌ Error previewing file '{file.filename}' by '{current_user}': {str(e)}")
        raise HTTPException(status_code=500, detail="Preview failed due to a server error.")
