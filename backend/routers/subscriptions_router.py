"""Управление приобретёнными абонементами клиентов."""
from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_any_staff, require_manager
from ..database import db_cursor
from ..schemas import ClientSubscriptionIn, ClientSubscriptionOut

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


_LIST_SQL = """
SELECT
    cs.id,
    cs.client_id,
    c.full_name           AS client_full_name,
    cs.subscription_type_id,
    st.name               AS subscription_name,
    cs.purchase_date,
    cs.start_date,
    cs.end_date,
    cs.lessons_left,
    cs.status,
    cs.price_paid
FROM client_subscriptions cs
JOIN clients c           ON c.id  = cs.client_id
JOIN subscription_types st ON st.id = cs.subscription_type_id
"""


@router.get("", response_model=list[ClientSubscriptionOut])
def list_subscriptions(client_id: Optional[int] = None, _=Depends(require_any_staff)):
    sql = _LIST_SQL + (" WHERE cs.client_id = ?" if client_id else "") + " ORDER BY cs.purchase_date DESC"
    params = (client_id,) if client_id else ()
    with db_cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


@router.post("", response_model=ClientSubscriptionOut, status_code=201)
def sell_subscription(payload: ClientSubscriptionIn, user: dict = Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT duration_days, lessons_count, price FROM subscription_types WHERE id = ? AND is_active = 1",
            (payload.subscription_type_id,),
        )
        st = cur.fetchone()
        if st is None:
            raise HTTPException(400, "Тариф не найден или неактивен")

        end_date = payload.start_date + dt.timedelta(days=st["duration_days"])
        try:
            cur.execute(
                """INSERT INTO client_subscriptions
                   (client_id, subscription_type_id, purchase_date,
                    start_date, end_date, lessons_left, status,
                    sold_by_staff_id, price_paid)
                   VALUES (?, ?, CURRENT_DATE, ?, ?, ?, 'active', ?, ?)""",
                (payload.client_id, payload.subscription_type_id,
                 payload.start_date, end_date,
                 st["lessons_count"], user["id"], st["price"]),
            )
        except Exception as exc:
            raise HTTPException(400, f"Не удалось оформить абонемент: {exc}")

        new_id = cur.lastrowid
        cur.execute(_LIST_SQL + " WHERE cs.id = ?", (new_id,))
        return dict(cur.fetchone())


@router.post("/{subscription_id}/freeze", response_model=ClientSubscriptionOut)
def freeze(subscription_id: int, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE client_subscriptions SET status = 'frozen' WHERE id = ? AND status = 'active'",
            (subscription_id,),
        )
        if cur.rowcount == 0:
            raise HTTPException(400, "Абонемент не найден или не в статусе active")
        cur.execute(_LIST_SQL + " WHERE cs.id = ?", (subscription_id,))
        return dict(cur.fetchone())


@router.post("/{subscription_id}/resume", response_model=ClientSubscriptionOut)
def resume(subscription_id: int, _=Depends(require_manager)):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE client_subscriptions SET status = 'active' WHERE id = ? AND status = 'frozen'",
            (subscription_id,),
        )
        if cur.rowcount == 0:
            raise HTTPException(400, "Абонемент не найден или не заморожен")
        cur.execute(_LIST_SQL + " WHERE cs.id = ?", (subscription_id,))
        return dict(cur.fetchone())
