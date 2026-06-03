-- =====================================================
-- БАЗА ДАННЫХ "Спортивный клуб"
-- СУБД: SQLite 3.35+    Кодировка: UTF-8
-- Схема в 3НФ
-- =====================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA encoding     = 'UTF-8';

-- -------- 1. СПРАВОЧНИКИ -----------------------------

CREATE TABLE IF NOT EXISTS roles (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS staff (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT    NOT NULL,
    position      TEXT    NOT NULL,
    phone         TEXT,
    email         TEXT    UNIQUE,
    hire_date     DATE    NOT NULL,
    login         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role_id       INTEGER NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS clients (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name         TEXT    NOT NULL,
    birth_date        DATE,
    gender            TEXT    CHECK (gender IN ('М', 'Ж')),
    phone             TEXT    UNIQUE,
    email             TEXT,
    registration_date DATE    NOT NULL DEFAULT CURRENT_DATE,
    notes             TEXT,
    is_active         INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS trainers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT    NOT NULL,
    specialization TEXT,
    phone          TEXT,
    email          TEXT,
    hire_date      DATE    NOT NULL,
    bio            TEXT,
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS class_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT,
    color_code  TEXT    NOT NULL DEFAULT '#3F51B5'
);

CREATE TABLE IF NOT EXISTS halls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    capacity        INTEGER NOT NULL CHECK (capacity > 0),
    equipment_notes TEXT
);

CREATE TABLE IF NOT EXISTS subscription_types (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    description   TEXT,
    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
    lessons_count INTEGER CHECK (lessons_count IS NULL OR lessons_count > 0),
    price         NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- -------- 2. ОПЕРАЦИОННЫЕ ТАБЛИЦЫ --------------------

CREATE TABLE IF NOT EXISTS client_subscriptions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id            INTEGER NOT NULL,
    subscription_type_id INTEGER NOT NULL,
    purchase_date        DATE    NOT NULL DEFAULT CURRENT_DATE,
    start_date           DATE    NOT NULL,
    end_date             DATE    NOT NULL,
    lessons_left         INTEGER,
    status               TEXT    NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'expired', 'frozen', 'used_up', 'cancelled')),
    sold_by_staff_id     INTEGER NOT NULL,
    price_paid           NUMERIC(10, 2) NOT NULL CHECK (price_paid >= 0),
    CHECK (end_date >= start_date),
    FOREIGN KEY (client_id)            REFERENCES clients            (id) ON DELETE RESTRICT,
    FOREIGN KEY (subscription_type_id) REFERENCES subscription_types (id) ON DELETE RESTRICT,
    FOREIGN KEY (sold_by_staff_id)     REFERENCES staff              (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS classes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    class_type_id    INTEGER NOT NULL,
    trainer_id       INTEGER NOT NULL,
    hall_id          INTEGER NOT NULL,
    scheduled_date   DATE    NOT NULL,
    start_time       TEXT    NOT NULL,
    end_time         TEXT    NOT NULL,
    max_participants INTEGER NOT NULL CHECK (max_participants > 0),
    status           TEXT    NOT NULL DEFAULT 'scheduled'
        CHECK (status IN ('scheduled', 'held', 'cancelled')),
    CHECK (end_time > start_time),
    FOREIGN KEY (class_type_id) REFERENCES class_types (id) ON DELETE RESTRICT,
    FOREIGN KEY (trainer_id)    REFERENCES trainers    (id) ON DELETE RESTRICT,
    FOREIGN KEY (hall_id)       REFERENCES halls       (id) ON DELETE RESTRICT,
    UNIQUE (trainer_id, scheduled_date, start_time),
    UNIQUE (hall_id,    scheduled_date, start_time)
);

CREATE TABLE IF NOT EXISTS attendance (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id              INTEGER NOT NULL,
    class_id               INTEGER NOT NULL,
    client_subscription_id INTEGER NOT NULL,
    check_in_time          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recorded_by_staff_id   INTEGER NOT NULL,
    UNIQUE (client_id, class_id),
    FOREIGN KEY (client_id)              REFERENCES clients              (id) ON DELETE RESTRICT,
    FOREIGN KEY (class_id)               REFERENCES classes              (id) ON DELETE RESTRICT,
    FOREIGN KEY (client_subscription_id) REFERENCES client_subscriptions (id) ON DELETE RESTRICT,
    FOREIGN KEY (recorded_by_staff_id)   REFERENCES staff                (id) ON DELETE RESTRICT
);

-- -------- 3. ИНДЕКСЫ ---------------------------------

CREATE INDEX IF NOT EXISTS idx_subs_client   ON client_subscriptions (client_id);
CREATE INDEX IF NOT EXISTS idx_subs_status   ON client_subscriptions (status);
CREATE INDEX IF NOT EXISTS idx_subs_end_date ON client_subscriptions (end_date);
CREATE INDEX IF NOT EXISTS idx_classes_date  ON classes              (scheduled_date);
CREATE INDEX IF NOT EXISTS idx_att_class     ON attendance           (class_id);
CREATE INDEX IF NOT EXISTS idx_att_client    ON attendance           (client_id);

-- -------- 4. ТРИГГЕРЫ БИЗНЕС-ЛОГИКИ -------------------

DROP TRIGGER IF EXISTS trg_attendance_validate;
CREATE TRIGGER trg_attendance_validate
BEFORE INSERT ON attendance
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT status FROM client_subscriptions
                  WHERE id = NEW.client_subscription_id) != 'active'
                THEN RAISE(ABORT, 'Абонемент не находится в статусе active')
            WHEN (SELECT client_id FROM client_subscriptions
                  WHERE id = NEW.client_subscription_id) != NEW.client_id
                THEN RAISE(ABORT, 'Абонемент принадлежит другому клиенту')
            WHEN (SELECT end_date FROM client_subscriptions
                  WHERE id = NEW.client_subscription_id) < DATE('now')
                THEN RAISE(ABORT, 'Срок действия абонемента истёк')
            WHEN COALESCE((SELECT lessons_left FROM client_subscriptions
                  WHERE id = NEW.client_subscription_id), 1) <= 0
                THEN RAISE(ABORT, 'Все занятия абонемента исчерпаны')
        END;
END;

DROP TRIGGER IF EXISTS trg_attendance_decrement;
CREATE TRIGGER trg_attendance_decrement
AFTER INSERT ON attendance
FOR EACH ROW
BEGIN
    UPDATE client_subscriptions
       SET lessons_left = lessons_left - 1
     WHERE id = NEW.client_subscription_id
       AND lessons_left IS NOT NULL;

    UPDATE client_subscriptions
       SET status = 'used_up'
     WHERE id = NEW.client_subscription_id
       AND lessons_left = 0;
END;

DROP TRIGGER IF EXISTS trg_attendance_restore;
CREATE TRIGGER trg_attendance_restore
AFTER DELETE ON attendance
FOR EACH ROW
BEGIN
    UPDATE client_subscriptions
       SET lessons_left = lessons_left + 1,
           status       = CASE WHEN status = 'used_up' THEN 'active' ELSE status END
     WHERE id = OLD.client_subscription_id
       AND lessons_left IS NOT NULL;
END;
