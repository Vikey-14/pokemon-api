import logging
import os
import sys

# 📁 Create logs/ folder if not exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 🛡️ Enable UTF-8 console output for emojis (safe fallback)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass  # Safe fallback for older Python versions

# 🔴 Error Logger: Logs all ERROR-level events
error_logger = logging.getLogger("api_error")
if not error_logger.hasHandlers():  # ✅ Prevent duplicate handlers on reload
    error_handler = logging.FileHandler(f"{LOG_DIR}/error_log.txt", encoding="utf-8")
    error_handler.setFormatter(logging.Formatter("[%(asctime)s] [ERROR] %(message)s"))
    error_logger.setLevel(logging.ERROR)
    error_logger.addHandler(error_handler)

# 🟢 Info Logger: General info and audit events
info_logger = logging.getLogger("api_info")
if not info_logger.hasHandlers():  # ✅ Prevent duplicate handlers on reload
    info_handler = logging.FileHandler(f"{LOG_DIR}/api_info.log", encoding="utf-8")
    info_handler.setFormatter(logging.Formatter("[%(asctime)s] [INFO] %(message)s"))
    info_logger.setLevel(logging.INFO)
    info_logger.addHandler(info_handler)


