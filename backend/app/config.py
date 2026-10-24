
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CERT_PATH = certifi.where()

if not os.path.isfile(CERT_PATH):
    raise FileNotFoundError(
        f"CA certificate bundle not found: {CERT_PATH}"
    )

os.environ["SSL_CERT_FILE"] = CERT_PATH

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash",
)
