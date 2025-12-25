from __future__ import annotations

from sqlalchemy import select

from ..db import SessionLocal
from ..models import Role


def list_roles() -> list[Role]:
    session = SessionLocal()
    return session.execute(select(Role).order_by(Role.name)).scalars().all()


def get_role(role_id: int) -> Role | None:
    session = SessionLocal()
    return session.get(Role, role_id)


def create_role(name: str, instruction: str | None) -> tuple[Role | None, str | None]:
    if not name:
        return None, "Имя обязательно."

    session = SessionLocal()
    exists = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if exists:
        return None, "Роль с таким именем уже существует."

    role = Role(name=name, instruction=instruction)
    session.add(role)
    session.commit()
    return role, None


def update_role(role_id: int, name: str, instruction: str | None) -> tuple[Role | None, str | None]:
    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        return None, "Роль не найдена."

    if not name:
        return None, "Имя обязательно."

    exists = (
        session.execute(select(Role).where(Role.name == name, Role.id != role_id))
        .scalar_one_or_none()
    )
    if exists:
        return None, "Роль с таким именем уже существует."

    role.name = name
    role.instruction = instruction
    session.commit()
    return role, None


def delete_role(role_id: int) -> str | None:
    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        return "Роль не найдена."

    session.delete(role)
    session.commit()
    return None
