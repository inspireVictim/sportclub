"""Управление расписанием занятий."""
from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_any_staff, require_manager
from ..database import db_cursor
from ..schemas import ClassIn, ClassOut

router = APIRouter(prefix="/api/classes", tags=["classes"])


_LIST_SQL = """
SELECT
    c.id,
    c.class_type_id,
    ct.name              AS class_type_name,
    ct.color_code        AS class_type_color,
    c.trainer_id,
    t.full_name          AS trainer_full_name,
    c.hall_id,
    h.name               AS hall_name,
    c.scheduled_date,
    c.start_time,
    c.end_time,
    c.max_participants,
    c.status,
    (SELECT COUNT(*) FROM attendance a WHERE a.class_id = c.id) AS attendees_count
FROM classes c
JOIN class_types ct ON ct.id = c.class_type_id
JOIN trainers     t  ON t.id  = c.trainer_id
JOIN halls        h  ON h.id  = c.hall_id
"""


@router.get("", response_model=list[ClassOut])
def list_classes(
    date_from: Optional[dt.date] = None,
    date_to: Optional[dt.date] = None,
    _=Depends(require_any_staff),
):
    sql = _LIST_SQL
    params: "list" = []
    if date_from and date_to:
        sql += " WHERE c.scheduled_date BETWEEN ? AND ?"
        params += [date_from, date_to]
    elif date_from:
        sql += " WHERE c.scheduled_date >= ?"
        params.append(date_from)
    sql += " ORDER BY c.scheduled_date, c.start_time"
    with db_cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


@router.post("", response_model=ClassOut, status_code=201)
def create_class(payload: ClassIn, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        try:
            cur.execute(
                """INSERT INTO classes
                   (class_type_id, trainer_id, hall_id, scheduled_date,
                    start_time, end_time, max_participants)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (payload.class_type_id, payload.trainer_id, payload.hall_id,
                 payload.scheduled_date, payload.start_time, payload.end_time,
                 payload.max_participants),
            )
        except Exception as exc:
            raise HTTPException(
                400,
                f"Конфликт расписания: тренер или зал уже заняты на это время ({exc})",
            )
        new_id = cur.lastrowid
        cur.execute(_LIST_SQL + " WHERE c.id = ?", (new_id,))
        return dict(cur.fetchone())


@router.delete("/{class_id}", status_code=204)
def cancel_class(class_id: int, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT COUNT(*) AS c FROM attendance WHERE class_id = ?", (class_id,))
        if cur.fetchone()["c"] > 0:
            cur.execute("UPDATE classes SET status = 'cancelled' WHERE id = ?", (class_id,))
        else:
            cur.execute("DELETE FROM classes WHERE id = ?", (class_id,))
            if cur.rowcount == 0:
                raise HTTPException(404, "Занятие не найдено")
    return None
