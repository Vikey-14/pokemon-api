from utils.limiter import limiter
from config import settings  # assuming `settings.TESTING` is available

def limit_safe(rate: str):
    """
    Smart limiter that disables itself in test mode.
    """
    if settings.TESTING:
        print(f"🧪 [Limiter] Skipping rate limit ({rate}) in TESTING mode.")
        return lambda f: f  # no-op decorator
    else:
        return limiter.limit(rate, key_func=lambda req: req.client.host or "fallback-ip")

