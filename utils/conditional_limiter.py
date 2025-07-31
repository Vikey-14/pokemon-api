# utils/conditional_limiter.py
import os
from utils.limiter import limiter

TESTING = os.getenv("TESTING", "0") == "1"

def conditional_limit(rate: str):
    return (lambda func: func) if TESTING else limiter.limit(rate)
