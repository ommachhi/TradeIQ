from __future__ import annotations

import os
import re
from datetime import datetime, timezone

import bcrypt
import jwt
import streamlit as st

from utils.constants import JWT_EXPIRY


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,}$")
MOBILE_PATTERN = re.compile(r"^[0-9]{7,15}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch((email or "").strip()))


def validate_password(password: str) -> bool:
    return bool(PASSWORD_PATTERN.fullmatch(password or ""))


def validate_mobile(mobile: str) -> bool:
    return bool(MOBILE_PATTERN.fullmatch((mobile or "").strip()))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def get_jwt_secret() -> str:
    if "jwt_secret" in st.secrets:
        return st.secrets["jwt_secret"]
    return os.getenv("TREDALQ_JWT_SECRET", "tredalq-dev-secret-change-me-please-rotate")


def create_token(user: dict) -> str:
    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "iat": issued_at,
        "exp": issued_at + JWT_EXPIRY,
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    return payload
