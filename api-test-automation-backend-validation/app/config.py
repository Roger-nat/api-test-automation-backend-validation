from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(ROOT_DIR / 'qa_test_management.db').as_posix()}",
)
APP_ENV = os.getenv("APP_ENV", "development")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dev-only-change-me-before-deployment",
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

LLM_API_URL = os.getenv("LLM_API_URL") or None
LLM_API_KEY = os.getenv("LLM_API_KEY") or None
LLM_MODEL = os.getenv("LLM_MODEL") or None
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
