"""CRUD-эндпоинты для клиентов."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_any_staff, require_manager
from ..database import db_cursor
from ..schemas import ClientIn, ClientOut

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
def list_clients(_=Depends(require_any_staff)):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM clients ORDER BY full_name")
        return [dict(r) for r in cur.fetchall()]


@router.post("", response_model=ClientOut, status_code=201)
def create_client(payload: ClientIn, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        try:
            cur.execute(
                """INSERT INTO clients
                   (full_name, birth_date, gender, phone, email, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (payload.full_name, payload.birth_date, payload.gender,
                 payload.phone, payload.email, payload.notes),
            )
        except Exception as exc:
            raise HTTPException(400, f"Не удалось создать клиента: {exc}")
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM clients WHERE id = ?", (new_id,))
        return dict(cur.fetchone())


@router.put("/{client_id}", response_model=ClientOut)
def update_client(client_id: int, payload: ClientIn, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE clients
               SET full_name = ?, birth_date = ?, gender = ?,
                   phone = ?, email = ?, notes = ?
               WHERE id = ?""",
            (payload.full_name, payload.birth_date, payload.gender,
             payload.phone, payload.email, payload.notes, client_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Клиент не найден")
        cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        return dict(cur.fetchone())


@router.delete("/{client_id}", status_code=204)
def deactivate_client(client_id: int, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE clients SET is_active = 0 WHERE id = ?", (client_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Клиент не найден")
    return None
