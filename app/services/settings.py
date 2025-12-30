from __future__ import annotations

from sqlalchemy import select

from ..db import SessionLocal
from ..models import Parameter

SETTINGS_KEYS = ("API_KEY", "MODEL", "INSTRUCTIONS", "CONFIG")
_KEY_FIELD_MAP = {
    "API_KEY": "api_key",
    "MODEL": "model",
    "INSTRUCTIONS": "instructions",
    "CONFIG": "config",
}


def list_parameters() -> list[Parameter]:
    session = SessionLocal()
    return session.execute(select(Parameter).order_by(Parameter.id)).scalars().all()


def get_parameter(parameter_id: int) -> Parameter | None:
    session = SessionLocal()
    return session.get(Parameter, parameter_id)


def get_parameter_value(key: str) -> str | None:
    if not key:
        return None
    field_name = _KEY_FIELD_MAP.get(key)
    if not field_name:
        return None
    session = SessionLocal.session_factory()
    try:
        row = session.execute(select(Parameter)).scalars().first()
        if not row:
            return None
        return getattr(row, field_name)
    finally:
        session.close()


def get_settings_values(keys: tuple[str, ...] = SETTINGS_KEYS) -> dict[str, str]:
    session = SessionLocal()
    row = session.execute(select(Parameter)).scalars().first()
    if not row:
        return {key: "" for key in keys}
    values = {}
    for key in keys:
        field_name = _KEY_FIELD_MAP.get(key)
        values[key] = getattr(row, field_name) if field_name else ""
    return values


def update_settings(values: dict[str, str], keys: tuple[str, ...] = SETTINGS_KEYS) -> None:
    session = SessionLocal()
    row = session.execute(select(Parameter)).scalars().first()
    if not row:
        row = Parameter(
            api_key="",
            model="",
            instructions="",
            config="",
        )
        session.add(row)
        session.flush()
    for key in keys:
        field_name = _KEY_FIELD_MAP.get(key)
        if not field_name:
            continue
        setattr(row, field_name, values.get(key, ""))
    session.commit()


def create_parameter(key: str, value: str) -> tuple[Parameter | None, str | None]:
    if not key or not value:
        return None, "Ключ и значение обязательны."
    field_name = _KEY_FIELD_MAP.get(key)
    if not field_name:
        return None, "Неизвестный ключ."

    session = SessionLocal()
    row = session.execute(select(Parameter)).scalars().first()
    if not row:
        row = Parameter(
            api_key="",
            model="",
            instructions="",
            config="",
        )
        session.add(row)
        session.flush()
    setattr(row, field_name, value)
    session.commit()
    return row, None


def update_parameter(
    parameter_id: int, key: str, value: str
) -> tuple[Parameter | None, str | None]:
    session = SessionLocal()
    parameter = session.get(Parameter, parameter_id)
    if not parameter:
        return None, "Параметр не найден."

    if not key or not value:
        return None, "Ключ и значение обязательны."
    field_name = _KEY_FIELD_MAP.get(key)
    if not field_name:
        return None, "Неизвестный ключ."

    setattr(parameter, field_name, value)
    session.commit()
    return parameter, None


def delete_parameter(parameter_id: int) -> str | None:
    session = SessionLocal()
    parameter = session.get(Parameter, parameter_id)
    if not parameter:
        return "Параметр не найден."

    session.delete(parameter)
    session.commit()
    return None
