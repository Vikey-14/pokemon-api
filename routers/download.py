from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from auth.hybrid_auth import get_current_user
from utils.file_utils import verify_file_exists
from custom_logger import info_logger, error_logger  # ✅ Import both loggers
import os

router = APIRouter(tags=["Trainer View"])

#️⃣ Route to download battle log from server
@router.get(
    "/download/log",
    summary="Download battle log",
    description="Download the Pokémon battle log stored in logs folder. Requires authentication."
)
def download_battle_log(current_user: dict = Depends(get_current_user)):
    file_path = os.path.join("logs", "battle_log.txt")

    try:
        # 🧠 Ensure file exists, or raise 404
        verify_file_exists(file_path)

        # ✅ Log successful download
        info_logger.info(f"📥 Trainer '{current_user['username']}' downloaded 'battle_log.txt'.")

        return FileResponse(path=file_path, filename="battle_log.txt", media_type="text/plain")

    except FileNotFoundError as e:
        error_logger.error(f"❌ File not found for Trainer '{current_user['username']}': {str(e)}")
        raise HTTPException(status_code=404, detail="Battle log not found.")

    except Exception as e:
        error_logger.error(f"❌ Unexpected error in battle log download by '{current_user['username']}': {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading battle log.")
