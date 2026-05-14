import os
import traceback
from typing import Any, Callable, Optional

try:
    import psycopg2
    from psycopg2.extras import Json
except Exception as import_error:
    psycopg2 = None
    Json = None
    PSYCOPG_IMPORT_ERROR = import_error
else:
    PSYCOPG_IMPORT_ERROR = None


STORE_TABLE = "app_json_store"
_INIT_DONE = False


def _db_log(message: str) -> None:
    """
    Test-safe DB logger.
    In pytest, stay quiet.
    In Render/local app runs, print breadcrumbs.
    """
    if os.getenv("TESTING") != "1":
        print(message, flush=True)


def _db_bc(event: str, **fields) -> None:
    """
    Database breadcrumb logger.

    These breadcrumbs prove:
    - whether DATABASE_URL is being used
    - whether data is loading from Neon
    - whether data is saving to Neon
    - whether the app fell back to JSON files
    """
    try:
        safe_fields = {}

        for key, value in fields.items():
            if "url" in key.lower() or "password" in key.lower() or "secret" in key.lower():
                safe_fields[key] = "***hidden***"
            else:
                safe_fields[key] = value

        parts = " ".join(f"{k}={repr(v)}" for k, v in safe_fields.items())
        _db_log(f"[DB_BC] {event}" + (f" {parts}" if parts else ""))

    except Exception as e:
        _db_log(f"[DB_BC] {event} breadcrumb_error={type(e).__name__}:{e}")


def _database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


def db_enabled() -> bool:
    """
    DB is enabled only when DATABASE_URL exists and we are not in pytest mode.

    This preserves your local/test behavior:
    - Local without DATABASE_URL: old JSON files still work
    - Render with DATABASE_URL: Neon DB is used
    - Pytest: JSON/test files stay isolated
    """
    return bool(_database_url()) and os.getenv("TESTING") != "1"


def _get_connection():
    """
    Open a fresh PostgreSQL connection.

    We intentionally open short-lived connections for safety on Render Free.
    This avoids long stale connections after sleep/wake cycles.
    """
    if not db_enabled():
        raise RuntimeError("DATABASE_URL is not configured, DB storage is disabled.")

    if psycopg2 is None:
        _db_bc(
            "DB_IMPORT_MISSING",
            err_type=type(PSYCOPG_IMPORT_ERROR).__name__,
            err=str(PSYCOPG_IMPORT_ERROR),
        )
        raise RuntimeError(
            "psycopg2-binary is missing. Add psycopg2-binary==2.9.10 to requirements.txt"
        )

    try:
        conn = psycopg2.connect(_database_url(), connect_timeout=10)
        _db_bc("DB_CONNECT_OK")
        return conn

    except Exception as e:
        _db_bc(
            "DB_CONNECT_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        raise


def init_db() -> None:
    """
    Create the generic JSON storage table if it does not exist.

    We use one table with key/value JSON documents:
    - key='pokedex' stores full Pokédex
    - key='team' stores full team

    This keeps the migration low-risk and dynamic.
    Future fields inside Pokémon/team objects will persist automatically.
    """
    global _INIT_DONE

    if not db_enabled():
        _db_bc("DB_INIT_SKIPPED_DISABLED")
        return

    if _INIT_DONE:
        return

    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {STORE_TABLE} (
                        key TEXT PRIMARY KEY,
                        data JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )

        _INIT_DONE = True
        _db_bc("DB_INIT_OK", table=STORE_TABLE)

    except Exception as e:
        _db_bc(
            "DB_INIT_ERR",
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        raise


def load_json_document(
    key: str,
    fallback_loader: Callable[[], Any],
    expected_empty: Optional[Any] = None,
) -> Any:
    """
    Load one JSON document from Neon.

    If DATABASE_URL is not present:
        Use fallback_loader(), which means old JSON files still work locally.

    If DATABASE_URL is present but the DB has no row yet:
        Seed Neon once from the existing local JSON file.
    """
    if expected_empty is None:
        expected_empty = {}

    if not db_enabled():
        _db_bc("JSON_DOC_LOAD_FALLBACK_DB_DISABLED", key=key)
        return fallback_loader()

    init_db()

    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT data FROM {STORE_TABLE} WHERE key = %s;",
                    (key,),
                )
                row = cur.fetchone()

        if row is not None:
            data = row[0]
            _db_bc(
                "JSON_DOC_LOAD_DB_OK",
                key=key,
                data_type=type(data).__name__,
                size=len(data) if hasattr(data, "__len__") else None,
            )
            return data

        fallback_data = fallback_loader()

        if fallback_data is None:
            fallback_data = expected_empty

        _db_bc(
            "JSON_DOC_DB_EMPTY_SEEDING_FROM_FILE",
            key=key,
            fallback_type=type(fallback_data).__name__,
            fallback_size=len(fallback_data) if hasattr(fallback_data, "__len__") else None,
        )

        save_json_document(key, fallback_data)

        return fallback_data

    except Exception as e:
        _db_bc(
            "JSON_DOC_LOAD_DB_ERR",
            key=key,
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        raise


def save_json_document(key: str, data: Any) -> bool:
    """
    Save one JSON document to Neon.

    Returns:
    - True when saved to DB
    - False only when DB is disabled

    Important:
    If DATABASE_URL is configured but DB save fails, this raises.
    We do not silently fall back to local JSON in production because that
    would bring back the same disappearing-data bug.
    """
    if not db_enabled():
        _db_bc("JSON_DOC_SAVE_SKIPPED_DB_DISABLED", key=key)
        return False

    init_db()

    try:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {STORE_TABLE} (key, data, updated_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (key)
                    DO UPDATE SET
                        data = EXCLUDED.data,
                        updated_at = NOW();
                    """,
                    (key, Json(data)),
                )

        _db_bc(
            "JSON_DOC_SAVE_DB_OK",
            key=key,
            data_type=type(data).__name__,
            size=len(data) if hasattr(data, "__len__") else None,
        )
        return True

    except Exception as e:
        _db_bc(
            "JSON_DOC_SAVE_DB_ERR",
            key=key,
            err_type=type(e).__name__,
            err=str(e),
            traceback=traceback.format_exc(),
        )
        raise


def storage_debug() -> dict:
    """
    Small helper for logs/debugging.
    Does not expose DATABASE_URL.
    """
    return {
        "db_enabled": db_enabled(),
        "database_url_present": bool(_database_url()),
        "testing": os.getenv("TESTING") == "1",
        "table": STORE_TABLE,
        "psycopg2_loaded": psycopg2 is not None,
    }