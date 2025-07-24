from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from auth.hybrid_auth import role_required  # 🔐 RBAC
from utils.file_utils import is_csv_file
from custom_logger import info_logger, error_logger  # ✅ Both loggers
import csv
from io import StringIO
from file_handler import load_pokedex, save_pokedex

router = APIRouter(tags=["Admin Actions"])

#️⃣ Upload Pokémon data via CSV
@router.post(
    "/upload/csv",
    summary="Upload CSV to import Pokémon",
    description="Takes a .csv file and adds them to the Pokédex. Requires authentication."
)
def upload_csv(
    file: UploadFile = File(...),
    user=Depends(role_required("admin"))
):
    # ✅ Check file type
    if not is_csv_file(file):
        error_logger.error(f"❌ '{file.filename}' rejected by {user['username']}: Not a CSV")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted."
        )

    try:
        content = file.file.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(content))
    except Exception as e:
        error_logger.error(f"❌ CSV decoding failed for '{file.filename}' by {user['username']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSV content."
        )

    pokedex = load_pokedex()
    added = []

    # ✅ Process each row
    for row in csv_reader:
        try:
            new_id = max(pokedex.keys(), default=0) + 1
            pokedex[new_id] = row
            added.append(row["name"])
        except Exception as e:
            error_logger.warning(f"⚠️ Skipped malformed row in '{file.filename}': {row} | Error: {e}")
            continue

    # ✅ Save updated Pokédex
    save_pokedex(pokedex)

    info_logger.info(f"📊 Trainer '{user['username']}' uploaded CSV '{file.filename}' → {len(added)} Pokémon added: {added}")

    return JSONResponse(
        status_code=201,
        content={"message": f"{len(added)} Pokémon added!", "added": added}
    )
