from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from auth.hybrid_auth import role_required  # 🔐 Admin access control
from utils.file_utils import validate_file_upload  # ✅ File type + MIME check
from custom_logger import info_logger, error_logger
from utils.limiter_utils import limit_safe  # 🧪 Auto-disables during tests
import csv
from io import StringIO
from utils.file_handler import load_pokedex, save_pokedex

router = APIRouter(tags=["Admin Actions"])

#️⃣ Upload CSV to import Pokémon (basic secure version)
@router.post(
    "/upload/csv",
    summary="Upload CSV to import Pokémon",
    description="Takes a .csv file and adds them to the Pokédex. Requires authentication."
)
@limit_safe("5/minute")  # 🔁 Auto-handles TESTING mode
def upload_csv(
    request: Request, 
    file: UploadFile = File(...),
    user=Depends(role_required("admin"))
):
    try:
        # 🔐 Step 1: Securely validate file
        validate_file_upload(file)

        # ✅ Step 2: Decode CSV content (check encoding)
        content = file.file.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(content))

    except UnicodeDecodeError:
        error_logger.error(f"❌ File '{file.filename}' is not valid UTF-8. Uploaded by {user['username']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="❌ Invalid encoding. Only UTF-8 CSV files are allowed."
        )

    except HTTPException:
        raise  # ✅ Allow FastAPI to handle it

    except Exception as e:
        error_logger.error(f"❌ CSV parsing failed for '{file.filename}' by {user['username']}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="❌ Failed to read or parse CSV."
        )

    # 🔄 Step 3: Load Pokédex and add new Pokémon
    pokedex = load_pokedex()
    added = []

    for row in csv_reader:
        try:
            new_id = max(pokedex.keys(), default=0) + 1
            pokedex[new_id] = row
            added.append(row.get("name", "Unknown"))
        except Exception as e:
            error_logger.warning(f"⚠️ Skipped malformed row in '{file.filename}': {row} | Error: {e}")
            continue

    # 💾 Step 4: Save updates
    save_pokedex(pokedex)

    info_logger.info(
        f"📊 Trainer '{user['username']}' uploaded CSV '{file.filename}' → "
        f"{len(added)} Pokémon added: {added}"
    )

    return JSONResponse(
        status_code=201,
        content={"message": f"{len(added)} Pokémon added!", "added": added}
    )
