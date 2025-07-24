# upload.py (LEGACY MASTER FILE)
# --------------------------------------------------
# This was the original 400+ line upload module
# where all Pokémon upload, preview, image, gallery,
# and CSV import logic lived.
#
# Every route in this file has now been modularized
# into dedicated files inside the `routers/` folder:
# - upload_csv.py
# - upload_image.py
# - upload_image_secure.py
# - upload_misc.py
# - upload_csv_validated.py
# - gallery.py
# - download.py
#
# This file is no longer used by the app directly.
# It is preserved here as a memory of how the journey began —
# line by line, route by route, building the Pokémon API.
#
# 💡 Fun Fact: This file was once the entire backend.
# Now, it's the foundation of a production-grade modular system.
#

from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from typing import List
from datetime import datetime
import os, csv
from io import StringIO

from file_handler import load_pokedex, save_pokedex
from auth.security import verify_token  # 🔒 Token-based protection

router = APIRouter()
UPLOAD_DIR = "uploads"
pokedex = load_pokedex()

# ----------------------------
# 🔐 /upload/save (secure)
# ----------------------------
@router.post("/upload/save", tags=["Admin Actions"], summary="Save file to disk safely",
             description="Accepts a file and stores it in the uploads folder. Renames if already exists.")
async def save_uploaded_file(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)  # 🔒
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    return JSONResponse(content={
        "message": f"✅ File saved by {current_user}!",
        "original_name": original_name,
        "stored_as": new_filename,
        "path": file_path
    })


# ----------------------------
# 🔐 /upload/preview (secure)
# ----------------------------
@router.post("/upload/preview", tags=["Admin Actions"], summary="Read file without saving",
             description="Accepts a file and previews its content without storing it.")
async def preview_uploaded_file(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)  # 🔒
):
    content = await file.read()

    if file.content_type in ["text/plain", "text/csv"]:
        try:
            decoded = content.decode("utf-8")
            preview = decoded[:300]
            lines = preview.splitlines()[:10]
            return {
                "filename": file.filename,
                "uploaded_by": current_user,
                "content_type": file.content_type,
                "preview": lines
            }
        except UnicodeDecodeError:
            return {
                "filename": file.filename,
                "error": "❌ Failed to decode file. Not valid UTF-8 text."
            }

    elif file.content_type.startswith("image/"):
        return {
            "filename": file.filename,
            "uploaded_by": current_user,
            "message": "🖼️ Image uploaded. No preview available."
        }

    return {
        "filename": file.filename,
        "uploaded_by": current_user,
        "message": "❌ Unsupported file type for preview."
    }


# ----------------------------
# 🔐 /upload/csv-import (secure)
# ----------------------------
@router.post("/upload/csv-import", tags=["Admin Actions"], summary="Validated CSV Pokédex Import",
             description="Parses and validates a CSV file and imports Pokémon.")
async def import_pokedex_csv(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)  # 🔒
):
    if not file.filename.endswith(".csv"):
        return {"error": "Only CSV files are allowed!"}

    try:
        content = await file.read()
        decoded = content.decode("utf-8")
        csv_reader = csv.DictReader(StringIO(decoded))

        added = 0
        failed = 0
        duplicate_skipped = 0
        failed_details = []

        for row in csv_reader:
            try:
                poke_id = int(row["id"])
                name = row["name"].strip()
                ptype = row["type"].strip()
                level = int(row["level"])

                if poke_id in pokedex:
                    duplicate_skipped += 1
                    failed_details.append({"row": row, "error": f"Duplicate ID {poke_id}"})
                    continue
                if not name or not ptype:
                    failed += 1
                    failed_details.append({"row": row, "error": "Missing name or type"})
                    continue
                if level < 5 or level > 100:
                    failed += 1
                    failed_details.append({"row": row, "error": f"Invalid level {level}"})
                    continue

                pokedex[poke_id] = {"name": name, "type": ptype, "level": level}
                added += 1

            except Exception as e:
                failed += 1
                failed_details.append({"row": row, "error": f"Exception: {str(e)}"})

        save_pokedex(pokedex)

        return {
            "message": f"CSV uploaded by {current_user}!",
            "added": added,
            "duplicates_skipped": duplicate_skipped,
            "failed_rows": failed,
            "details": failed_details,
            "total_in_pokedex": len(pokedex)
        }

    except Exception as e:
        return {"error": f"Failed to parse CSV: {str(e)}"}


# ----------------------------
# 🔐 /upload/secure-image (secure)
# ----------------------------
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
MAX_FILE_SIZE_MB = 2

@router.post("/upload/secure-image", tags=["Admin Actions"], summary="Secure Upload Pokémon Image",
             description="Uploads an image and returns preview in Swagger.", response_class=HTMLResponse)
async def upload_pokemon_image(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)  # 🔒
):
    if not file.content_type.startswith("image/"):
        return HTMLResponse("<h3>❌ Only image files are allowed.</h3>", status_code=400)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return HTMLResponse(f"<h3>❌ Unsupported file type: {ext}</h3>", status_code=400)

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return HTMLResponse(f"<h3>❌ File too large: {size_mb:.2f} MB</h3>", status_code=400)

    image_dir = os.path.join(UPLOAD_DIR, "images")
    os.makedirs(image_dir, exist_ok=True)

    original_name = file.filename
    file_path = os.path.join(image_dir, original_name)

    if os.path.exists(file_path):
        name_part, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{name_part}_{timestamp}{ext}"
        file_path = os.path.join(image_dir, new_filename)
    else:
        new_filename = original_name
        file_path = os.path.join(image_dir, new_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    image_url = f"/uploads/images/{new_filename}"
    html_response = f"""
    <h2>✅ Image Uploaded by {current_user}!</h2>
    <ul>
        <li><strong>Stored As:</strong> {new_filename}</li>
        <li><strong>Preview URL:</strong> <a href="{image_url}" target="_blank">{image_url}</a></li>
    </ul>
    <img src="{image_url}" width="300" style="border:1px solid #999; border-radius:6px;" />
    """

    return HTMLResponse(content=html_response)


# ----------------------------
# 🔐 /upload/multi-image (secure)
# ----------------------------
@router.post("/upload/multi-image", tags=["Admin Actions"], response_class=HTMLResponse,
             summary="Upload Multiple Images", description="Upload many Pokémon images together.")
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: str = Depends(verify_token)  # 🔒
):
    image_dir = os.path.join(UPLOAD_DIR, "images")
    os.makedirs(image_dir, exist_ok=True)

    uploaded_files = []

    for file in files:
        if not file.content_type.startswith("image/"):
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue

        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            continue

        original_name = file.filename
        file_path = os.path.join(image_dir, original_name)

        if os.path.exists(file_path):
            name, ext = os.path.splitext(original_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(image_dir, new_filename)
        else:
            new_filename = original_name
            file_path = os.path.join(image_dir, new_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        uploaded_files.append({
            "new_name": new_filename,
            "size": round(size_mb, 2),
            "url": f"/uploads/images/{new_filename}"
        })

    if not uploaded_files:
        return HTMLResponse("<h3>❌ No valid image files uploaded.</h3>", status_code=400)

    html = f"<h2>✅ Uploaded by {current_user}</h2><div style='display:flex; flex-wrap:wrap;'>"
    for file in uploaded_files:
        html += f"""
        <div style='margin:10px; text-align:center;'>
            <img src='{file["url"]}' width='200' style='border:1px solid #aaa; border-radius:8px;'><br>
            <p>{file["new_name"]} ({file["size"]} MB)</p>
        </div>
        """
    html += "</div>"
    return HTMLResponse(content=html)


# ----------------------------
# 🔐 /gallery (secure)
# ----------------------------
@router.get("/gallery", response_class=HTMLResponse, tags=["Admin Actions"], summary="View Pokémon Gallery",
            description="Shows all uploaded Pokémon images.")
async def view_gallery(
    current_user: str = Depends(verify_token)  # 🔒
):
    image_dir = os.path.join(UPLOAD_DIR, "images")
    if not os.path.exists(image_dir):
        return HTMLResponse("<h2>No images found.</h2>")

    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]

    if not image_files:
        return HTMLResponse("<h2>No Pokémon images have been uploaded yet.</h2>")

    html = f"<h2>🖼️ {current_user}'s Gallery</h2><hr><div style='display:flex; flex-wrap:wrap;'>"
    for image in image_files:
        img_path = f"/uploads/images/{image}"
        html += f"""
        <div style='margin:10px; text-align:center;'>
            <img src='{img_path}' width='200'><br>
            <p>{image}</p>
        </div>
        """
    html += "</div>"
    return HTMLResponse(content=html)


# ----------------------------
# 🔐 /download/log (secure)
# ----------------------------
@router.get("/download/log", tags=["Trainer View"], summary="Download battle log",
            description="Download the Pokémon battle log stored in logs folder.")
def download_battle_log(current_user: str = Depends(verify_token)):  # 🔒
    file_path = os.path.join("logs", "battle_log.txt")
    if not os.path.exists(file_path):
        return {"error": "Log file not found."}
    return FileResponse(path=file_path, filename="battle_log.txt", media_type="text/plain")


# ----------------------------
# 🔐 /upload/csv (secure)
# ----------------------------
@router.post("/upload/csv", tags=["Admin Actions"], summary="Upload and import Pokémon CSV",
             description="Accepts a CSV file and adds it to the Pokédex.")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: str = Depends(verify_token)  # 🔒
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))

    added = 0
    skipped = 0
    failed = 0
    details = []

    for row in reader:
        try:
            poke_id = int(row["id"])
            name = row["poke_name"].strip()
            ptype = row["Type"].strip()
            level = int(row["level"])

            if poke_id in pokedex:
                skipped += 1
                details.append({"id": poke_id, "status": "❌ Duplicate ID"})
                continue
            if not name or not ptype:
                failed += 1
                details.append({"id": poke_id, "status": "❌ Missing name/type"})
                continue
            if level < 5 or level > 100:
                failed += 1
                details.append({"id": poke_id, "status": "❌ Invalid level"})
                continue

            pokedex[poke_id] = {"poke_name": name, "Type": ptype, "level": level}
            added += 1
            details.append({"id": poke_id, "status": "✅ Added"})

        except Exception as e:
            failed += 1
            details.append({"row": row, "status": f"❌ Error: {str(e)}"})

    save_pokedex(pokedex)

    return {
        "message": f"✅ CSV processed by {current_user}!",
        "added": added,
        "skipped": skipped,
        "failed": failed,
        "details": details
    }
