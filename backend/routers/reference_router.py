"""Простые справочники: классы занятий, залы, тарифы."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_any_staff, require_admin
from ..database import db_cursor
from ..schemas import ClassTypeOut, HallOut, SubscriptionTypeIn, SubscriptionTypeOut

router = APIRouter(prefix="/api", tags=["references"])


@router.get("/class_types", response_model=list[ClassTypeOut])
def list_class_types(_=Depends(require_any_staff)):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM class_types ORDER BY name")
        return [dict(r) for r in cur.fetchall()]


@router.get("/halls", response_model=list[HallOut])
def list_halls(_=Depends(require_any_staff)):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM halls ORDER BY name")
        return [dict(r) for r in cur.fetchall()]


@router.get("/subscription_types", response_model=list[SubscriptionTypeOut])
def list_subscription_types(_=Depends(require_any_staff)):
    with db_cursor() as cur:
        cur.execute(
            "SELECT * FROM subscription_types WHERE is_active = 1 ORDER BY price"
        )
        return [dict(r) for r in cur.fetchall()]


@router.post("/subscription_types", response_model=SubscriptionTypeOut, status_code=201)
def create_subscription_type(payload: SubscriptionTypeIn, _=Depends(require_admin)):
    with db_cursor(commit=True) as cur:
        try:
            cur.execute(
                """INSERT INTO subscription_types
                   (name, description, duration_days, lessons_count, price)
                   VALUES (?, ?, ?, ?, ?)""",
                (payload.name, payload.description, payload.duration_days,
                 payload.lessons_count, payload.price),
            )
        except Exception as exc:
            raise HTTPException(400, f"Не удалось создать тариф: {exc}")
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM subscription_types WHERE id = ?", (new_id,))
        return dict(cur.fetchone())
