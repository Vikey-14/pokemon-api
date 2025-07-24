from fastapi import UploadFile, HTTPException, status
from datetime import datetime
from config import settings  # ✅ Import environment settings
import os

#️⃣ Check if uploaded file has .csv extension
def is_csv_file(file: UploadFile) -> bool:
    return file.filename.lower().endswith(".csv")

#️⃣ Check if uploaded file is an image based on MIME type
def is_image_file(file: UploadFile) -> bool:
    return file.content_type.startswith(settings.ALLOWED_IMAGE_TYPES)  # ✅ From .env

#️⃣ Add a timestamp prefix to the filename
def generate_timestamped_filename(original_name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{original_name}"

#️⃣ Build the full path using upload directory from env
def get_upload_path(filename: str) -> str:
    return os.path.join(settings.UPLOAD_DIR, generate_timestamped_filename(filename))

#️⃣ Raise a 404 error if the given file path does not exist
def verify_file_exists(filepath: str):
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filepath}"
        )
