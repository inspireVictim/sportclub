"""Ключевой алгоритм: фиксация посещения занятия клиентом.

Сценарий выполнения единой транзакции:
    1. Найти активный действующий абонемент клиента, по которому он может
       посетить данное занятие (по дате и остатку занятий).
    2. Вставить запись в attendance.
    3. Триггеры СУБД (trg_attendance_validate) перепроверяют целостность;
       триггер trg_attendance_decrement автоматически уменьшает lessons_left;
       при обнулении lessons_left статус абонемента переводится в 'used_up'.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_any_staff
from ..database import db_cursor
from ..schemas import AttendanceIn, AttendanceOut

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


_LIST_SQL = """
SELECT
    a.id,
    a.client_id,
    cl.full_name        AS client_full_name,
    a.class_id,
    ct.name             AS class_type_name,
    c.scheduled_date,
    c.start_time,
    a.client_subscription_id,
    a.check_in_time,
    s.full_name         AS recorded_by
FROM attendance a
JOIN clients     cl ON cl.id = a.client_id
JOIN classes     c  ON c.id  = a.class_id
JOIN class_types ct ON ct.id = c.class_type_id
JOIN staff       s  ON s.id  = a.recorded_by_staff_id
"""


def _pick_active_subscription(cur, client_id: int, scheduled_date) -> Optional[int]:
    """Подбор подходящего абонемента: активный, со сроком, со свободным остатком.

    Приоритет — у абонементов с минимальным остатком (или с самой ранней
    датой окончания), чтобы они расходовались первыми и не «протухали».
    """
    cur.execute(
        """SELECT id, lessons_left, end_date
             FROM client_subscriptions
            WHERE client_id = ?
              AND status    = 'active'
              AND start_date <= ?
              AND end_date   >= ?
              AND (lessons_left IS NULL OR lessons_left > 0)
            ORDER BY
                CASE WHEN lessons_left IS NULL THEN 1 ELSE 0 END,
                lessons_left ASC,
                end_date ASC
            LIMIT 1""",
        (client_id, scheduled_date, scheduled_date),
    )
    row = cur.fetchone()
    return row["id"] if row else None


@router.get("", response_model=list[AttendanceOut])
def list_attendance(class_id: Optional[int] = None, _=Depends(require_any_staff)):
    sql = _LIST_SQL + (" WHERE a.class_id = ?" if class_id else "")
    params = (class_id,) if class_id else ()
    sql += " ORDER BY a.check_in_time DESC"
    with db_cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


@router.post("", response_model=AttendanceOut, status_code=201)
def register_attendance(payload: AttendanceIn, user: dict = Depends(require_any_staff)):
    with db_cursor(commit=True) as cur:
        # Получаем дату занятия и проверяем существование
        cur.execute(
            "SELECT scheduled_date, status, max_participants FROM classes WHERE id = ?",
            (payload.class_id,),
        )
        cls = cur.fetchone()
        if cls is None:
            raise HTTPException(404, "Занятие не найдено")
        if cls["status"] != "scheduled":
            raise HTTPException(400, "Занятие отменено или уже проведено")

        # Контроль вместимости занятия
        cur.execute("SELECT COUNT(*) AS c FROM attendance WHERE class_id = ?", (payload.class_id,))
        if cur.fetchone()["c"] >= cls["max_participants"]:
            raise HTTPException(400, "Достигнут предел вместимости занятия")

        # Подбор подходящего абонемента
        subscription_id = _pick_active_subscription(cur, payload.client_id, cls["scheduled_date"])
        if subscription_id is None:
            raise HTTPException(
                400,
                "У клиента нет действующего абонемента, по которому можно записать посещение",
            )

        try:
            cur.execute(
                """INSERT INTO attendance
                   (client_id, class_id, client_subscription_id, recorded_by_staff_id)
                   VALUES (?, ?, ?, ?)""",
                (payload.client_id, payload.class_id, subscription_id, user["id"]),
            )
        except Exception as exc:
            # Триггеры СУБД возвращают сообщения через ABORT
            raise HTTPException(400, f"Невозможно зафиксировать посещение: {exc}")

        new_id = cur.lastrowid
        cur.execute(_LIST_SQL + " WHERE a.id = ?", (new_id,))
        return dict(cur.fetchone())


@router.delete("/{attendance_id}", status_code=204)
def revoke_attendance(attendance_id: int, _=Depends(require_any_staff)):
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Запись посещения не найдена")
    return None
