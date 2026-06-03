"""Эндпоинты аутентификации."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import (
    create_token,
    get_current_user,
    verify_password,
)
from ..database import db_cursor
from ..schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    with db_cursor() as cur:
        cur.execute(
            """SELECT s.id, s.full_name, s.login, s.password_hash, s.is_active, r.code AS role
               FROM staff s JOIN roles r ON r.id = s.role_id
               WHERE s.login = ?""",
            (payload.login,),
        )
        row = cur.fetchone()
        if row is None or row["is_active"] != 1:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")
        if not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")

        token = create_token(row["id"], row["login"], row["role"])
        return TokenResponse(
            access_token=token,
            user_id=row["id"],
            full_name=row["full_name"],
            role=row["role"],
        )


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "full_name": user["full_name"], "role": user["role"]}
