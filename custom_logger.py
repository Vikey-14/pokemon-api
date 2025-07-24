# custom_logger.py
import logging
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Make sure logs/ folder exists

# 🔴 Error logger setup
error_logger = logging.getLogger("api_error")
error_handler = logging.FileHandler(f"{LOG_DIR}/error_log.txt")
error_format = logging.Formatter("[%(asctime)s] [ERROR] %(message)s")
error_handler.setFormatter(error_format)
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

# 🟢 Info logger setup
info_logger = logging.getLogger("api_info")
info_handler = logging.FileHandler(f"{LOG_DIR}/api_info.log")
info_format = logging.Formatter("[%(asctime)s] [INFO] %(message)s")
info_handler.setFormatter(info_format)
info_logger.setLevel(logging.INFO)
info_logger.addHandler(info_handler)
