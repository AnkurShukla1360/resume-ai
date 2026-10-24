
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from langchain_groq import ChatGroq


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env", override=True)

# Use a valid CA certificate bundle for HTTPS requests.
CERT_PATH = certifi.where()
os.environ["SSL_CERT_FILE"] = CERT_PATH
os.environ["REQUESTS_CA_BUNDLE"] = CERT_PATH

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)


def get_llm(model: str | None = None):
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY missing. Check backend/.env"
        )

    return ChatGroq(
        model=model or GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0,
        max_retries=2,
        timeout=60,
    )
