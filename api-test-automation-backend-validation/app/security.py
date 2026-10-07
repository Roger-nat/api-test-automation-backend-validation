from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash a password using scrypt from Python's standard library."""
    salt = os.urandom(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )
    return "scrypt$16384$8$1${salt}${hash}".format(
        salt=base64.urlsafe_b64encode(salt).decode("ascii"),
        hash=base64.urlsafe_b64encode(derived).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, n, r, p, salt_text, hash_text = stored.split("$", 5)
        if algorithm != "scrypt":
            return False

        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(hash_text.encode("ascii"))

        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (jwt.InvalidTokenError, TypeError, ValueError):
        return None
