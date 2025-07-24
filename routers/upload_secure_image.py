from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from auth.hybrid_auth import role_required  # 🔐 RBAC imported from here
from custom_logger import info_logger, error_logger  # ✅ Import both loggers
from datetime import datetime
from typing import List
import os

router = APIRouter(tags=["Admin Actions"])

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
MAX_FILE_SIZE_MB = 2
image_dir = os.path.join(UPLOAD_DIR, "images")
os.makedirs(image_dir, exist_ok=True)

#️⃣ Upload a single secure image with validations + HTML preview
@router.post("/upload/secure-image", summary="Secure Upload Pokémon Image", response_class=HTMLResponse)
async def upload_pokemon_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(role_required("admin"))
):
    if not file.content_type.startswith("image/"):
        error_logger.error(f"❌ Invalid content type '{file.content_type}' uploaded by {current_user['username']}")
        return HTMLResponse("<h3>❌ Only image files are allowed.</h3>", status_code=400)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        error_logger.error(f"❌ Unsupported extension '{ext}' by {current_user['username']}")
        return HTMLResponse(f"<h3>❌ Unsupported file type: {ext}</h3>", status_code=400)

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        error_logger.error(f"❌ Oversized file ({size_mb:.2f} MB) by {current_user['username']}")
        return HTMLResponse(f"<h3>❌ File too large: {size_mb:.2f} MB</h3>", status_code=400)

    filename = file.filename
    if os.path.exists(os.path.join(image_dir, filename)):
        name_part, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name_part}_{timestamp}{ext}"

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


#️⃣ Upload multiple images at once with validation
@router.post("/upload/multi-image", summary="Upload Multiple Images", response_class=HTMLResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(role_required("admin"))
):
    uploaded_files = []

    for file in files:
        if not file.content_type.startswith("image/"):
            error_logger.error(f"❌ Skipped file '{file.filename}': Invalid content type by {current_user['username']}")
            continue

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            error_logger.error(f"❌ Skipped file '{file.filename}': Unsupported extension '{ext}' by {current_user['username']}")
            continue

        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            error_logger.error(f"❌ Skipped file '{file.filename}': Too large ({size_mb:.2f} MB) by {current_user['username']}")
            continue

        filename = file.filename
        if os.path.exists(os.path.join(image_dir, filename)):
            name_part, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name_part}_{timestamp}{ext}"

        file_path = os.path.join(image_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)

        uploaded_files.append({
            "new_name": filename,
            "size": round(size_mb, 2),
            "url": f"/uploads/images/{filename}"
        })

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
