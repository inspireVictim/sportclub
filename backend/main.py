"""Точка входа FastAPI-приложения «Спортивный клуб»."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import init_schema, seed_data
from .routers import (
    attendance_router,
    auth_router,
    classes_router,
    clients_router,
    reference_router,
    subscriptions_router,
    trainers_router,
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(
    title="Спортивный клуб — REST API",
    description="ВКР. Бэкенд для управления БД спортивного клуба.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_schema()
    seed_data()


app.include_router(auth_router.router)
app.include_router(clients_router.router)
app.include_router(trainers_router.router)
app.include_router(reference_router.router)
app.include_router(subscriptions_router.router)
app.include_router(classes_router.router)
app.include_router(attendance_router.router)


# Раздача статического фронтенда
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def root_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/dashboard")
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "pages" / "dashboard.html")
