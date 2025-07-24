from fastapi import APIRouter, UploadFile, File, Depends, status
from fastapi.responses import JSONResponse
from auth.security import verify_token
from datetime import datetime
from custom_logger import info_logger  # ✅ Import logger
import os

router = APIRouter(tags=["Admin Actions"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#️⃣ Save any file to disk (renames if it already exists)
@router.post("/upload/save", summary="Save file to disk safely")
async def save_uploaded_file(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)
):
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

    # ✅ Log the file save
    info_logger.info(f"💾 File '{original_name}' saved by '{current_user}' as '{new_filename}'")

    return JSONResponse(content={
        "message": f"✅ File saved by {current_user}!",
        "original_name": original_name,
        "stored_as": new_filename,
        "path": file_path
    })


#️⃣ Preview text or image file content without saving
@router.post("/upload/preview", summary="Read file without saving")
async def preview_uploaded_file(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)
):
    content = await file.read()

    if file.content_type in ["text/plain", "text/csv"]:
        try:
            decoded = content.decode("utf-8")
            preview = decoded[:300]
            lines = preview.splitlines()[:10]

            # ✅ Log preview
            info_logger.info(f"👁️ Previewed text file '{file.filename}' by '{current_user}'")

            return {
                "filename": file.filename,
                "uploaded_by": current_user,
                "content_type": file.content_type,
                "preview": lines
            }
        except UnicodeDecodeError:
            info_logger.warning(f"⚠️ Failed to decode '{file.filename}' uploaded by '{current_user}'")

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

    info_logger.info(f"⛔ Unsupported preview type for file '{file.filename}' by '{current_user}'")

    return {
        "filename": file.filename,
        "uploaded_by": current_user,
        "message": "❌ Unsupported file type for preview."
    }
