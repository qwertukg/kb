# KB Admin

Минимальная админка для ролей, агентов, досок, статусов и задач (Flask + SQLAlchemy + Alembic + Bootstrap).

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

Откройте в браузере: http://127.0.0.1:8008

## Запуск в Docker

```bash
docker build -t kb .
docker run --rm -p 8008:8008 kb
```

Чтобы контейнер работал с локальной SQLite-базой, смонтируйте файл:

```bash
docker run --rm -p 8008:8008 \
  -v /Users/daniil/Projects/kb/kb.db:/app/kb.db \
  kb
```

## Сиды (опционально)

```bash
python scripts/seed.py
```

Скрипт заполнит тестовые данные и добавит несколько сообщений к каждой задаче.

## Поля задач

- `Заголовок` — обязательный текстовый заголовок задачи.

## Переменные окружения (опционально)

- `DATABASE_URL` — строка подключения (по умолчанию `sqlite:///kb.db`)
- `SECRET_KEY` — секретный ключ Flask (по умолчанию `dev-secret`)
- `TRUSTED_HOSTS` — список разрешенных хостов через запятую (по умолчанию `localhost,127.0.0.1,0.0.0.0,::1`)
