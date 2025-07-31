from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from auth.hybrid_auth import role_required  # 🔐 Role-based access control
from utils.file_handler import load_pokedex, save_pokedex
from custom_logger import info_logger, error_logger  # ✅ Loggers
from utils.file_utils import validate_file_upload  # 🔐 Security validation
from utils.limiter_utils import limit_safe  # ✅ Import safe limiter for test bypass
from io import StringIO
import csv

router = APIRouter(tags=["Admin Actions"])

#️⃣ Validated CSV import with test-safe rate limiting
@router.post("/upload/csv-import", summary="Validated CSV Pokédex Import")
@limit_safe("5/minute")  # ✅ Bypassed in TESTING mode
async def import_pokedex_csv(
    request: Request, 
    file: UploadFile = File(...),
    current_user: str = Depends(role_required("admin"))
):
    try:
        # 🔐 Step 1: Validate file extension, MIME type, size
        validate_file_upload(file)

        # ✅ Step 2: Decode CSV content
        content = await file.read()
        decoded = content.decode("utf-8")
        csv_reader = csv.DictReader(StringIO(decoded))

        # 🔄 Step 3: Load and process each row
        pokedex = load_pokedex()
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

                # ❌ Duplicate ID
                if poke_id in pokedex:
                    duplicate_skipped += 1
                    failed_details.append({"row": row, "error": f"Duplicate ID {poke_id}"})
                    continue

                # ❌ Missing data
                if not name or not ptype:
                    failed += 1
                    failed_details.append({"row": row, "error": "Missing name or type"})
                    continue

                # ❌ Invalid level
                if level < 5 or level > 100:
                    failed += 1
                    failed_details.append({"row": row, "error": f"Invalid level {level}"})
                    continue

                # ✅ Add to Pokédex
                pokedex[poke_id] = {"name": name, "type": ptype, "level": level}
                added += 1

            except Exception as e:
                failed += 1
                failed_details.append({"row": row, "error": f"Exception: {str(e)}"})
                error_logger.warning(
                    f"⚠️ Row skipped in '{file.filename}': {row} | Error: {e}"
                )

        # 💾 Save Pokédex
        save_pokedex(pokedex)

        # 📜 Log results
        info_logger.info(
            f"📥 Validated CSV '{file.filename}' uploaded by '{current_user}' → "
            f"✅ Added: {added}, ⚠️ Duplicates: {duplicate_skipped}, ❌ Failed: {failed}"
        )

        return {
            "message": f"CSV uploaded by {current_user}!",
            "added": added,
            "duplicates_skipped": duplicate_skipped,
            "failed_rows": failed,
            "details": failed_details,
            "total_in_pokedex": len(pokedex)
        }

    except HTTPException:
        raise  # ✅ Pass through known exceptions

    except Exception as e:
        error_logger.error(f"❌ Critical CSV parsing failure by {current_user}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse CSV: {str(e)}")
