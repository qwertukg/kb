# KB Admin

Минимальная админка для сущности "Роль" (Flask + SQLAlchemy + Alembic + Bootstrap).

## Зависимости

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

## Запуск

```bash
alembic upgrade head
python -m app
```

Откройте в браузере: http://127.0.0.1:5000

## Переменные окружения (опционально)

- `DATABASE_URL` — строка подключения (по умолчанию `sqlite:///kb.db`)
- `SECRET_KEY` — секретный ключ Flask (по умолчанию `dev-secret`)
