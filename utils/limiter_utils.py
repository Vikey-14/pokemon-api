from typing import Any

from utils.limiter import limiter
from config import settings


def _lim_bc(event: str, **fields) -> None:
    try:
        parts = " ".join(f"{k}={repr(v)}" for k, v in fields.items())
        print(f"[LIM_BC] {event}" + (f" {parts}" if parts else ""), flush=True)
    except Exception as e:
        print(f"[LIM_BC] {event} breadcrumb_error={type(e).__name__}:{e}", flush=True)


def _safe_req_path(request: Any) -> str | None:
    try:
        return getattr(getattr(request, "url", None), "path", None)
    except Exception:
        return None


def _safe_limit_key(request: Any) -> str:
    """
    Robust key extractor for SlowAPI.
    Never raises; always returns a usable limiter key.
    """
    try:
        if request is None:
            _lim_bc("LIMIT_KEY_NO_REQUEST", chosen="fallback-ip")
            return "fallback-ip"

        client = getattr(request, "client", None)
        host = getattr(client, "host", None)

        headers = getattr(request, "headers", {}) or {}
        xff = headers.get("x-forwarded-for") if hasattr(headers, "get") else None
        xri = headers.get("x-real-ip") if hasattr(headers, "get") else None

        if xff:
            chosen = xff.split(",")[0].strip()
        elif xri:
            chosen = xri.strip()
        elif host:
            chosen = host
        else:
            chosen = "fallback-ip"

        _lim_bc(
            "LIMIT_KEY_OK",
            path=_safe_req_path(request),
            host=host,
            xff=xff,
            xri=xri,
            chosen=chosen,
        )
        return chosen

    except Exception as e:
        _lim_bc(
            "LIMIT_KEY_ERR",
            path=_safe_req_path(request),
            err_type=type(e).__name__,
            err=str(e),
            chosen="fallback-ip",
        )
        return "fallback-ip"


def limit_safe(rate: str):
    """
    Smart limiter:
    - no-op in TESTING
    - production-safe key function
    - breadcrumbs at build/attach/runtime key extraction
    """
    _lim_bc(
        "LIMIT_BUILD",
        rate=rate,
        testing=settings.TESTING,
        app_env=getattr(settings, "APP_ENV", None),
    )

    if settings.TESTING:
        print(f"🧪 [Limiter] Skipping rate limit ({rate}) in TESTING mode.", flush=True)
        return lambda f: f

    def decorator(func):
        func_name = getattr(func, "__qualname__", getattr(func, "__name__", repr(func)))
        _lim_bc("LIMIT_ATTACH_BEGIN", rate=rate, func=func_name)

        try:
            limited = limiter.limit(rate, key_func=_safe_limit_key)(func)
            _lim_bc("LIMIT_ATTACH_OK", rate=rate, func=func_name)
            return limited
        except Exception as e:
            _lim_bc(
                "LIMIT_ATTACH_ERR",
                rate=rate,
                func=func_name,
                err_type=type(e).__name__,
                err=str(e),
            )
            raise

    return decorator