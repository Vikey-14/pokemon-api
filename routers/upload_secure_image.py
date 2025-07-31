from fastapi import APIRouter, UploadFile, File, Depends, Request
from fastapi.responses import HTMLResponse
from utils.limiter_utils import limit_safe  # ✅ Safe limiter for testing
from auth.hybrid_auth import role_required  # 🔐 Admin-only access
from custom_logger import info_logger, error_logger
from utils.file_utils import validate_file_upload
from datetime import datetime
from typing import List
import os

router = APIRouter(tags=["Admin Actions"])

UPLOAD_DIR = "uploads"
image_dir = os.path.join(UPLOAD_DIR, "images")
os.makedirs(image_dir, exist_ok=True)  # ✅ Ensure parent dir exists at startup

#️⃣ Upload a single secure image with validations + HTML preview
@router.post("/upload/secure-image", summary="Secure Upload Pokémon Image", response_class=HTMLResponse)
@limit_safe("3/minute")  # ✅ Test-safe limiter
async def upload_pokemon_image(
    request: Request, 
    file: UploadFile = File(...),
    current_user: dict = Depends(role_required("admin"))
):
    try:
        validate_file_upload(file)
        content = await file.read()
        filename = file.filename

        # 🕓 Rename if file already exists
        if os.path.exists(os.path.join(image_dir, filename)):
            name_part, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name_part}_{timestamp}{ext}"

        # ✅ Ensure image directory exists inside test runs too
        os.makedirs(image_dir, exist_ok=True)

        # 💾 Save file
        file_path = os.path.join(image_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)

        image_url = f"/uploads/images/{filename}"
        info_logger.info(f"🛡️ Secure image '{file.filename}' uploaded by {current_user['username']} → saved as '{filename}'.")

        return HTMLResponse(f"""
        <h2>✅ Image Uploaded by {current_user['username']}!</h2>
        <ul>
            <li><strong>Stored As:</strong> {filename}</li>
            <li><strong>Preview URL:</strong> <a href="{image_url}" target="_blank">{image_url}</a></li>
        </ul>
        <img src="{image_url}" width="300" style="border:1px solid #999; border-radius:6px;" />
        """)

    except Exception as e:
        error_logger.error(f"❌ Upload failed: {str(e)}")
        return HTMLResponse(f"<h3>❌ Upload failed: {str(e)}</h3>", status_code=400)


#️⃣ Upload multiple images at once with validation
@router.post("/upload/multi-image", summary="Upload Multiple Images", response_class=HTMLResponse)
@limit_safe("2/minute")  # ✅ Test-safe limiter
async def upload_multiple_images(
    request: Request, 
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(role_required("admin"))
):
    uploaded_files = []

    for file in files:
        try:
            validate_file_upload(file)
            content = await file.read()
            filename = file.filename

            if os.path.exists(os.path.join(image_dir, filename)):
                name_part, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name_part}_{timestamp}{ext}"

            # ✅ Ensure image directory exists inside test runs too
            os.makedirs(image_dir, exist_ok=True)

            file_path = os.path.join(image_dir, filename)
            with open(file_path, "wb") as f:
                f.write(content)

            size_mb = round(len(content) / (1024 * 1024), 2)
            uploaded_files.append({
                "new_name": filename,
                "size": size_mb,
                "url": f"/uploads/images/{filename}"
            })

        except Exception as e:
            error_logger.error(f"❌ Skipped file '{file.filename}': {str(e)}")

    if not uploaded_files:
        error_logger.error(f"❌ No valid image files uploaded by {current_user['username']}")
        return HTMLResponse("<h3>❌ No valid image files uploaded.</h3>", status_code=400)

    uploaded_names = [file["new_name"] for file in uploaded_files]
    info_logger.info(f"🛡️ Trainer '{current_user['username']}' uploaded {len(uploaded_names)} images: {uploaded_names}")

    html = f"<h2>✅ Uploaded by {current_user['username']}</h2><div style='display:flex; flex-wrap:wrap;'>"
    for file in uploaded_files:
        html += f"""
        <div style='margin:10px; text-align:center;'>
            <img src='{file["url"]}' width='200' style='border:1px solid #aaa; border-radius:8px;'><br>
            <p>{file["new_name"]} ({file["size"]} MB)</p>
        </div>
        """
    html += "</div>"
    return HTMLResponse(content=html)
