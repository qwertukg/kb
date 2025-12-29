from __future__ import annotations

from sqlalchemy import select

from ..db import SessionLocal
from ..models import Parameter


def list_parameters() -> list[Parameter]:
    session = SessionLocal()
    return session.execute(select(Parameter).order_by(Parameter.key)).scalars().all()


def get_parameter(parameter_id: int) -> Parameter | None:
    session = SessionLocal()
    return session.get(Parameter, parameter_id)


def get_parameter_value(key: str) -> str | None:
    if not key:
        return None
    session = SessionLocal.session_factory()
    try:
        return session.execute(
            select(Parameter.value).where(Parameter.key == key)
        ).scalar_one_or_none()
    finally:
        session.close()


def create_parameter(key: str, value: str) -> tuple[Parameter | None, str | None]:
    if not key or not value:
        return None, "Ключ и значение обязательны."

    session = SessionLocal()
    exists = session.execute(select(Parameter).where(Parameter.key == key)).scalar_one_or_none()
    if exists:
        return None, "Параметр с таким ключом уже существует."

    parameter = Parameter(key=key, value=value)
    session.add(parameter)
    session.commit()
    return parameter, None


def update_parameter(
    parameter_id: int, key: str, value: str
) -> tuple[Parameter | None, str | None]:
    session = SessionLocal()
    parameter = session.get(Parameter, parameter_id)
    if not parameter:
        return None, "Параметр не найден."

    if not key or not value:
        return None, "Ключ и значение обязательны."

    exists = (
        session.execute(
            select(Parameter).where(Parameter.key == key, Parameter.id != parameter_id)
        )
        .scalar_one_or_none()
    )
    if exists:
        return None, "Параметр с таким ключом уже существует."

    parameter.key = key
    parameter.value = value
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
