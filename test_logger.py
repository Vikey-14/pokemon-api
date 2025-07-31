# test_logger.py

import logging
import os

test_log_path = "logs/test_info.log"
os.makedirs("logs", exist_ok=True)

test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers in pytest reruns
if not test_logger.handlers:
    handler = logging.FileHandler(test_log_path, mode="w", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    test_logger.addHandler(handler)
