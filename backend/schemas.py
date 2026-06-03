"""Pydantic-схемы валидации входящих и исходящих данных."""
from __future__ import annotations

import datetime as dt
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


# ---------- Аутентификация ----------

class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    role: str


# ---------- Клиенты ----------

class ClientIn(BaseModel):
    full_name: str = Field(min_length=3, max_length=200)
    birth_date: Optional[dt.date] = None
    gender: Optional[Literal["М", "Ж"]] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = None


class ClientOut(ClientIn):
    id: int
    registration_date: dt.date
    is_active: int


# ---------- Тренеры ----------

class TrainerIn(BaseModel):
    full_name: str
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    hire_date: dt.date
    bio: Optional[str] = None


class TrainerOut(TrainerIn):
    id: int
    is_active: int


# ---------- Справочники ----------

class ClassTypeOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color_code: str


class HallOut(BaseModel):
    id: int
    name: str
    capacity: int
    equipment_notes: Optional[str]


class SubscriptionTypeIn(BaseModel):
    name: str
    description: Optional[str] = None
    duration_days: int = Field(gt=0)
    lessons_count: Optional[int] = Field(default=None, gt=0)
    price: float = Field(ge=0)


class SubscriptionTypeOut(SubscriptionTypeIn):
    id: int
    is_active: int


# ---------- Абонементы клиента ----------

class ClientSubscriptionIn(BaseModel):
    client_id: int
    subscription_type_id: int
    start_date: dt.date


class ClientSubscriptionOut(BaseModel):
    id: int
    client_id: int
    client_full_name: str
    subscription_type_id: int
    subscription_name: str
    purchase_date: dt.date
    start_date: dt.date
    end_date: dt.date
    lessons_left: Optional[int]
    status: str
    price_paid: float


# ---------- Расписание ----------

class ClassIn(BaseModel):
    class_type_id: int
    trainer_id: int
    hall_id: int
    scheduled_date: dt.date
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    max_participants: int = Field(gt=0)

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: str, info):
        st = info.data.get("start_time")
        if st and v <= st:
            raise ValueError("end_time должен быть строго позже start_time")
        return v


class ClassOut(BaseModel):
    id: int
    class_type_id: int
    class_type_name: str
    class_type_color: str
    trainer_id: int
    trainer_full_name: str
    hall_id: int
    hall_name: str
    scheduled_date: dt.date
    start_time: str
    end_time: str
    max_participants: int
    status: str
    attendees_count: int


# ---------- Посещения ----------

class AttendanceIn(BaseModel):
    client_id: int
    class_id: int


class AttendanceOut(BaseModel):
    id: int
    client_id: int
    client_full_name: str
    class_id: int
    class_type_name: str
    scheduled_date: dt.date
    start_time: str
    client_subscription_id: int
    check_in_time: dt.datetime
    recorded_by: str
