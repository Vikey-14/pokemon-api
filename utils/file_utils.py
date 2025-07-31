from fastapi import UploadFile, HTTPException, status
from datetime import datetime
import os

# --------------------------------------------------------------------------------
# 📁 FILE TYPE CHECKS & VALIDATION
# --------------------------------------------------------------------------------

def is_csv_file(file: UploadFile) -> bool:
    return file.filename.lower().endswith(".csv")

def is_image_file(file: UploadFile) -> bool:
    from config import settings  # ✅ Delayed import
    return file.content_type.startswith(settings.ALLOWED_IMAGE_TYPES)

def generate_timestamped_filename(original_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{original_name}"

def get_upload_path(filename: str) -> str:
    from config import settings  # ✅ Delayed import
    return os.path.join(settings.UPLOAD_DIR, generate_timestamped_filename(filename))

def verify_file_exists(filepath: str):
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filepath}"
        )

# --------------------------------------------------------------------------------
# 🔐 FILE VALIDATION LOGIC
# --------------------------------------------------------------------------------

def validate_file_upload(file: UploadFile):
    ALLOWED_EXTENSIONS = {
        ".csv": "text/csv",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"
    }
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"❌ File type '{ext}' not allowed. Must be CSV or image only."
        )

    expected_mime = ALLOWED_EXTENSIONS[ext]
    if file.content_type != expected_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"❌ MIME type mismatch. Expected {expected_mime}, got {file.content_type}."
        )

    content = file.file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="❌ File too large. Max allowed size is 2MB."
        )
    file.file.seek(0)
    return True

def validate_generic_file(file: UploadFile):
    from config import settings  # ✅ Delayed import

    ext = os.path.splitext(file.filename)[1].lower()
    SAFE_UPLOAD_EXTENSIONS = {
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"
    }
    MAX_SAFE_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

    if ext not in SAFE_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"❌ File type '{ext}' not allowed."
        )

    expected_mime = SAFE_UPLOAD_EXTENSIONS[ext]

    if not settings.TESTING and file.content_type != expected_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"❌ MIME mismatch. Expected '{expected_mime}', got '{file.content_type}'"
        )

    content = file.file.read(MAX_SAFE_UPLOAD_SIZE + 1)
    if not settings.TESTING and len(content) > MAX_SAFE_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="❌ File too large. Max 5MB allowed."
        )

    file.file.seek(0)
    return True

# --------------------------------------------------------------------------------
# 💾 FILE SAVING
# --------------------------------------------------------------------------------

def save_file(file: UploadFile, destination_dir: str) -> str:
    os.makedirs(destination_dir, exist_ok=True)
    filename = generate_timestamped_filename(file.filename)
    filepath = os.path.join(destination_dir, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    file.file.seek(0)
    return filename
