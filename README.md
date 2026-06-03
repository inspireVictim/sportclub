# Спортивный клуб — БД и веб-приложение (ВКР)

## Стек
- SQLite 3.35+
- Python 3.10+ / FastAPI / Pydantic 2
- HTML5 / CSS3 / Vanilla JS (Fetch API)

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Инициализация БД
python backend/init_db.py

# Запуск сервера
uvicorn backend.main:app --reload --port 8001
```

Откройте `http://localhost:8001/` в браузере.

## Учётные записи
- `admin` / `admin123` — администратор системы
- `manager` / `manager123` — менеджер (продаёт абонементы, ведёт расписание)
- `reception` / `reception123` — ресепшн (только фиксация посещений)

## Сборка ПЗ
```bash
python scripts/generate_pz.py
```
Результат: `ПЗ_База_Данных_Спортклуба.docx`
