"""Аутентификация и разграничение доступа на основе JWT."""
from __future__ import annotations

import os
import datetime as dt
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .database import db_cursor

JWT_SECRET = os.environ.get("JWT_SECRET", "sportclub-dev-secret-change-in-prod")
JWT_ALG = "HS256"
JWT_LIFETIME_HOURS = 12

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_token(user_id: int, login: str, role_code: str) -> str:
    payload = {
        "sub": str(user_id),
        "login": login,
        "role": role_code,
        "exp": dt.datetime.utcnow() + dt.timedelta(hours=JWT_LIFETIME_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
        )
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
        )

    with db_cursor() as cur:
        cur.execute(
            """SELECT s.id, s.full_name, s.login, s.is_active, r.code AS role
               FROM staff s JOIN roles r ON r.id = s.role_id
               WHERE s.id = ?""",
            (int(payload["sub"]),),
        )
        row = cur.fetchone()
        if row is None or row["is_active"] != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Учётная запись недоступна",
            )
        return dict(row)


def require_roles(*allowed: str):
    """Возвращает зависимость FastAPI, допускающую только указанные роли."""

    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции",
            )
        return user

    return dependency


require_admin = require_roles("admin")
require_manager = require_roles("admin", "manager")
require_any_staff = require_roles("admin", "manager", "receptionist")
