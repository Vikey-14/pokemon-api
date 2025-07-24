from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from auth.hybrid_auth import role_required  # 🔐 RBAC
from file_handler import load_pokedex, save_pokedex
from custom_logger import info_logger, error_logger  # ✅ Both loggers
from io import StringIO
import csv

router = APIRouter(tags=["Admin Actions"])

#️⃣ Validated CSV import with checks
@router.post("/upload/csv-import", summary="Validated CSV Pokédex Import")
async def import_pokedex_csv(
    file: UploadFile = File(...),
    current_user: str = Depends(role_required("admin"))
):
    if not file.filename.endswith(".csv"):
        error_logger.error(f"❌ '{file.filename}' rejected by {current_user}: Not a CSV")
        raise HTTPException(status_code=400, detail="Only CSV files are allowed!")

    try:
        content = await file.read()
        decoded = content.decode("utf-8")
        csv_reader = csv.DictReader(StringIO(decoded))

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
                error_logger.warning(f"⚠️ Row skipped in '{file.filename}': {row} | Error: {e}")

        save_pokedex(pokedex)

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

    except Exception as e:
        error_logger.error(f"❌ Critical CSV parsing failure by {current_user}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse CSV: {str(e)}")
