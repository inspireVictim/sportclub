"""Управление подключением к SQLite и инициализация схемы."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "data" / "sportclub.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_cursor(commit: bool = False):
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def seed_data() -> None:
    """Заполнение справочников и демонстрационных данных."""
    from .auth import hash_password

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM roles")
        if cur.fetchone()[0] > 0:
            return

        cur.executemany(
            "INSERT INTO roles (code, name) VALUES (?, ?)",
            [
                ("admin", "Администратор системы"),
                ("manager", "Менеджер"),
                ("receptionist", "Администратор ресепшн"),
            ],
        )

        cur.executemany(
            """INSERT INTO staff
               (full_name, position, phone, email, hire_date, login, password_hash, role_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("Иванов Иван Иванович", "Директор", "+996700111222",
                 "admin@club.kg", "2024-01-15", "admin", hash_password("admin123"), 1),
                ("Петрова Анна Сергеевна", "Менеджер", "+996700333444",
                 "manager@club.kg", "2024-03-01", "manager", hash_password("manager123"), 2),
                ("Сидоров Алексей Петрович", "Администратор", "+996700555666",
                 "reception@club.kg", "2024-05-10", "reception", hash_password("reception123"), 3),
            ],
        )

        cur.executemany(
            """INSERT INTO trainers
               (full_name, specialization, phone, hire_date, bio)
               VALUES (?, ?, ?, ?, ?)""",
            [
                ("Кузнецов Дмитрий Олегович", "Тяжёлая атлетика, силовой тренинг",
                 "+996701100200", "2024-02-01", "МСМК, 12 лет тренерского стажа"),
                ("Орлова Мария Викторовна", "Йога, пилатес, стретчинг",
                 "+996701100201", "2024-02-15", "Сертифицированный инструктор Yoga Alliance"),
                ("Беков Тимур Эркинович", "Кроссфит, функциональный тренинг",
                 "+996701100202", "2024-04-01", "CrossFit Level 2"),
                ("Алиева Жаныл Касымовна", "Танцевальные направления, зумба",
                 "+996701100203", "2024-06-10", "Чемпион КР по латиноамериканским танцам"),
            ],
        )

        cur.executemany(
            "INSERT INTO class_types (name, description, color_code) VALUES (?, ?, ?)",
            [
                ("Тренажёрный зал", "Свободное посещение тренажёрного зала", "#3F51B5"),
                ("Йога", "Групповое занятие по йоге", "#26A69A"),
                ("Кроссфит", "Функциональный тренинг высокой интенсивности", "#EF5350"),
                ("Зумба", "Танцевальная фитнес-программа", "#AB47BC"),
                ("Персональная тренировка", "Индивидуальное занятие с тренером", "#FFA726"),
            ],
        )

        cur.executemany(
            "INSERT INTO halls (name, capacity, equipment_notes) VALUES (?, ?, ?)",
            [
                ("Зал №1 «Силовой»", 25, "Силовые тренажёры, штанги, гантели"),
                ("Зал №2 «Групповой»", 20, "Зеркала, коврики, аудиосистема"),
                ("Зал №3 «Функциональный»", 15, "Канаты, кольца, ящики, гири"),
            ],
        )

        cur.executemany(
            """INSERT INTO subscription_types
               (name, description, duration_days, lessons_count, price)
               VALUES (?, ?, ?, ?, ?)""",
            [
                ("Безлимит на месяц", "Безлимитное посещение тренажёрного зала на 30 дней",
                 30, None, 3500.00),
                ("Безлимит на 3 месяца", "Безлимитное посещение тренажёрного зала на 90 дней",
                 90, None, 9000.00),
                ("Абонемент на 8 занятий", "8 групповых занятий любого направления (60 дней)",
                 60, 8, 2400.00),
                ("Абонемент на 12 занятий", "12 групповых занятий любого направления (90 дней)",
                 90, 12, 3300.00),
                ("Разовое посещение", "Однократное посещение тренажёрного зала",
                 1, 1, 500.00),
                ("Персональный пакет 10 тренировок", "10 индивидуальных тренировок с тренером",
                 120, 10, 12000.00),
            ],
        )

        cur.executemany(
            """INSERT INTO clients
               (full_name, birth_date, gender, phone, email, registration_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                ("Жапаров Нуртилек Талантович", "1998-04-12", "М",
                 "+996555000111", "nur@example.com", "2026-01-10"),
                ("Кадырова Айгерим Маратовна", "1995-09-05", "Ж",
                 "+996555000222", "aigerim@example.com", "2026-01-15"),
                ("Турсунов Айбек Жакыпович", "2001-12-20", "М",
                 "+996555000333", None, "2026-02-01"),
                ("Эркинбаева Айдай Эркиновна", "1999-06-30", "Ж",
                 "+996555000444", "aiday@example.com", "2026-02-12"),
                ("Бакыт уулу Эрлан", "1992-03-18", "М",
                 "+996555000555", None, "2026-03-05"),
                ("Осмонова Бегимай Канатовна", "2000-11-22", "Ж",
                 "+996555000666", "begim@example.com", "2026-03-20"),
                ("Шаймерденов Алмаз Бакытович", "1990-02-10", "М",
                 "+996555000777", None, "2026-04-01"),
            ],
        )

        cur.executemany(
            """INSERT INTO client_subscriptions
               (client_id, subscription_type_id, purchase_date, start_date, end_date,
                lessons_left, status, sold_by_staff_id, price_paid)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (1, 1, "2026-05-15", "2026-05-15", "2026-06-14", None, "active", 2, 3500.00),
                (2, 3, "2026-05-20", "2026-05-20", "2026-07-19", 8, "active", 2, 2400.00),
                (3, 5, "2026-06-01", "2026-06-01", "2026-06-30", 1, "active", 3, 500.00),
                (4, 4, "2026-04-10", "2026-04-10", "2026-07-09", 9, "active", 2, 3300.00),
                (5, 6, "2026-03-15", "2026-03-15", "2026-07-13", 6, "active", 2, 12000.00),
                (6, 3, "2026-05-25", "2026-05-25", "2026-07-24", 8, "active", 2, 2400.00),
                (7, 2, "2026-04-20", "2026-04-20", "2026-07-19", None, "active", 2, 9000.00),
            ],
        )

        cur.executemany(
            """INSERT INTO classes
               (class_type_id, trainer_id, hall_id, scheduled_date, start_time, end_time, max_participants)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (2, 2, 2, "2026-06-02", "08:00", "09:00", 20),
                (3, 3, 3, "2026-06-02", "10:00", "11:00", 15),
                (4, 4, 2, "2026-06-02", "18:00", "19:00", 20),
                (2, 2, 2, "2026-06-03", "08:00", "09:00", 20),
                (5, 1, 1, "2026-06-03", "12:00", "13:00", 1),
                (3, 3, 3, "2026-06-03", "19:00", "20:00", 15),
                (2, 2, 2, "2026-06-04", "08:00", "09:00", 20),
                (4, 4, 2, "2026-06-04", "18:00", "19:00", 20),
                (3, 3, 3, "2026-06-05", "10:00", "11:00", 15),
                (5, 1, 1, "2026-06-05", "14:00", "15:00", 1),
                (2, 2, 2, "2026-06-06", "09:00", "10:00", 20),
                (4, 4, 2, "2026-06-06", "11:00", "12:00", 20),
            ],
        )

        # Стартовые посещения (с прохождением триггеров)
        cur.executemany(
            """INSERT INTO attendance
               (client_id, class_id, client_subscription_id, recorded_by_staff_id)
               VALUES (?, ?, ?, ?)""",
            [
                (2, 1, 2, 3),
                (4, 1, 4, 3),
                (6, 1, 6, 3),
            ],
        )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_schema()
    seed_data()
    print(f"База данных создана: {DB_PATH}")
