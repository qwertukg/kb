#!/bin/sh
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_PATH="$ROOT_DIR/kb.db"

alembic upgrade head
python3 scripts/seed.py

docker build -t kb .
docker run --rm -p 8008:8008 \
  -v "$DB_PATH:/app/kb.db" \
  kb
