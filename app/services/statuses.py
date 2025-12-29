from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Column, Project, Status


def list_statuses() -> list[Status]:
    session = SessionLocal()
    return (
        session.execute(
            select(Status)
            .options(selectinload(Status.project))
            .order_by(Status.project_id, Status.name)
        )
        .scalars()
        .all()
    )


def get_status(status_id: int) -> Status | None:
    session = SessionLocal()
    return session.get(Status, status_id)


def get_form_projects() -> list[Project]:
    session = SessionLocal()
    return session.execute(select(Project).order_by(Project.name)).scalars().all()


def create_status(
    name: str,
    color: str,
    project_id: str,
) -> tuple[Status | None, str | None]:
    if not name or not project_id:
        return None, "Имя и проект обязательны."

    session = SessionLocal()
    project = session.get(Project, int(project_id))
    if not project:
        return None, "Проект не найден."

    status = Status(name=name, color=color or "#0d6efd", project_id=project.id)
    session.add(status)
    session.flush()

    max_position = session.execute(
        select(func.coalesce(func.max(Column.position), 0)).where(Column.project_id == project.id)
    ).scalar_one()
    session.add(
        Column(position=max_position + 1, project_id=project.id, status_id=status.id)
    )
    session.commit()
    return status, None


def update_status(
    status_id: int,
    name: str,
    color: str,
    project_id: str,
) -> tuple[Status | None, str | None]:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        return None, "Статус не найден."

    if not name or not project_id:
        return None, "Имя и проект обязательны."

    project = session.get(Project, int(project_id))
    if not project:
        return None, "Проект не найден."

    status.name = name
    status.color = color or "#0d6efd"
    column = status.column
    if not column:
        max_position = session.execute(
            select(func.coalesce(func.max(Column.position), 0)).where(
                Column.project_id == project.id
            )
        ).scalar_one()
        session.add(
            Column(position=max_position + 1, project_id=project.id, status_id=status.id)
        )
    elif status.project_id != project.id:
        max_position = session.execute(
            select(func.coalesce(func.max(Column.position), 0)).where(
                Column.project_id == project.id
            )
        ).scalar_one()
        column.project_id = project.id
        column.position = max_position + 1
    status.project_id = project.id
    session.commit()
    return status, None


def delete_status(status_id: int) -> str | None:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        return "Статус не найден."

    if status.column:
        session.delete(status.column)
    session.delete(status)
    session.commit()
    return None
