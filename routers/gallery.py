from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from auth.security import verify_token
from custom_logger import info_logger, error_logger
from utils.limiter_utils import limit_safe
import os

router = APIRouter(tags=["Admin Actions"])

#️⃣ View all uploaded Pokémon images in gallery form
@router.get("/gallery", response_class=HTMLResponse, summary="View Pokémon Gallery")
@limit_safe("5/minute")  # ✅ Safe limiter that disables in TESTING mode
async def view_gallery(request: Request, current_user: str = Depends(verify_token)):
    image_dir = os.path.join("uploads", "images")

    try:
        if not os.path.exists(image_dir):
            info_logger.info(f"📁 {current_user} accessed gallery – No folder found.")
            return HTMLResponse("<h2>No images found.</h2>")

        image_files = [
            f for f in os.listdir(image_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
        ]

        if not image_files:
            info_logger.info(f"📁 {current_user} accessed gallery - Folder exists but empty.")
            return HTMLResponse("<h2>No Pokémon images have been uploaded yet.</h2>")

        info_logger.info(f"🖼️ {current_user} viewed the Pokémon Gallery with {len(image_files)} images.")

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

    except Exception as e:
        error_logger.error(f"❌ Error in gallery route for '{current_user}': {str(e)}")
        return HTMLResponse(
            "<h2>⚠️ Unexpected error while loading the Pokémon Gallery.</h2>",
            status_code=500
        )
