from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from auth.hybrid_auth import get_current_user  
from utils.file_utils import is_image_file, generate_timestamped_filename
from custom_logger import info_logger, error_logger  # ✅ Both loggers imported
import os

router = APIRouter(tags=["Admin Actions"])

#️⃣ Create the image folder if it doesn't exist
UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#️⃣ Route to upload and save an image file
@router.post(
    "/upload/image",
    summary="Upload an image",
    description="Saves uploaded image to disk and returns filename. Requires authentication."
)
def upload_image(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    #️⃣ Validate content type
    if not is_image_file(file):
        error_logger.error(f"❌ Upload rejected: Invalid image file type '{file.filename}' by '{user.get('username', 'unknown')}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed.")

    #️⃣ Generate timestamped filename
    filename = generate_timestamped_filename(file.filename)
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        #️⃣ Save file to disk
        with open(filepath, "wb") as f:
            f.write(file.file.read())

        # ✅ Log the successful upload
        info_logger.info(f"🖼️ Image '{file.filename}' uploaded by Trainer '{user['username']}' → saved as '{filename}'.")

        return JSONResponse(status_code=201, content={"message": "Image uploaded!", "filename": filename})

    except Exception as e:
        error_logger.error(f"💥 Failed to save image '{file.filename}' by '{user.get('username', 'unknown')}': {str(e)}")
        raise HTTPException(status_code=500, detail="Image upload failed due to a server error.")
