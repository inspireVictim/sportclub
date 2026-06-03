"""CRUD-эндпоинты для тренеров."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_any_staff, require_admin
from ..database import db_cursor
from ..schemas import TrainerIn, TrainerOut

router = APIRouter(prefix="/api/trainers", tags=["trainers"])


@router.get("", response_model=list[TrainerOut])
def list_trainers(_=Depends(require_any_staff)):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM trainers ORDER BY full_name")
        return [dict(r) for r in cur.fetchall()]


@router.post("", response_model=TrainerOut, status_code=201)
def create_trainer(payload: TrainerIn, _=Depends(require_admin)):
    with db_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO trainers
               (full_name, specialization, phone, email, hire_date, bio)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (payload.full_name, payload.specialization, payload.phone,
             payload.email, payload.hire_date, payload.bio),
        )
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM trainers WHERE id = ?", (new_id,))
        return dict(cur.fetchone())


@router.delete("/{trainer_id}", status_code=204)
def deactivate_trainer(trainer_id: int, _=Depends(require_admin)):
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE trainers SET is_active = 0 WHERE id = ?", (trainer_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Тренер не найден")
    return None
