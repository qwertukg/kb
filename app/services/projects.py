from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Column, Project, Status


def list_projects() -> list[Project]:
    session = SessionLocal()
    return (
        session.execute(
            select(Project).options(selectinload(Project.board)).order_by(Project.name)
        )
        .scalars()
        .all()
    )


def get_project(project_id: int) -> Project | None:
    session = SessionLocal()
    return session.get(Project, project_id)


def get_project_with_board(project_id: int) -> Project | None:
    session = SessionLocal()
    return (
        session.execute(
            select(Project)
            .options(selectinload(Project.board).selectinload(Column.status))
            .where(Project.id == project_id)
        )
        .scalars()
        .first()
    )


def get_project_statuses(project_id: int) -> list[Status]:
    session = SessionLocal()
    return (
        session.execute(
            select(Status).where(Status.project_id == project_id).order_by(Status.name)
        )
        .scalars()
        .all()
    )


def create_project(
    name: str,
    board_rows: list[dict[str, str]] | None = None,
) -> tuple[Project | None, str | None]:
    if not name:
        return None, "Имя обязательно."

    session = SessionLocal()
    exists = session.execute(select(Project).where(Project.name == name)).scalar_one_or_none()
    if exists:
        return None, "Проект с таким именем уже существует."

    project = Project(name=name)
    session.add(project)
    session.flush()
    error = _sync_project_board(session, project, board_rows or [])
    if error:
        session.rollback()
        return None, error
    session.commit()
    return project, None


def update_project(
    project_id: int,
    name: str,
    board_rows: list[dict[str, str]] | None = None,
) -> tuple[Project | None, str | None]:
    session = SessionLocal()
    project = session.get(Project, project_id)
    if not project:
        return None, "Проект не найден."

    if not name:
        return None, "Имя обязательно."

    exists = (
        session.execute(select(Project).where(Project.name == name, Project.id != project_id))
        .scalar_one_or_none()
    )
    if exists:
        return None, "Проект с таким именем уже существует."

    project.name = name
    error = _sync_project_board(session, project, board_rows or [])
    if error:
        session.rollback()
        return None, error
    session.commit()
    return project, None


def delete_project(project_id: int) -> str | None:
    session = SessionLocal()
    project = session.get(Project, project_id)
    if not project:
        return "Проект не найден."

    session.delete(project)
    session.commit()
    return None


def _sync_project_board(
    session,
    project: Project,
    board_rows: list[dict[str, str]],
) -> str | None:
    seen_status_ids: set[int] = set()
    for row in board_rows:
        column_id = row.get("column_id", "").strip()
        status_id = row.get("status_id", "").strip()
        position_raw = row.get("position", "").strip()
        is_deleted = row.get("is_deleted", "").strip() == "1"

        if is_deleted:
            if column_id:
                column = session.get(Column, int(column_id))
                if not column or column.project_id != project.id:
                    return "Колонка не найдена."
                session.delete(column)
            continue

        if not status_id and not column_id:
            continue
        if not status_id:
            return "Статус колонки обязателен."
        if not position_raw:
            return "Позиция колонки обязательна."
        try:
            position_value = int(position_raw)
        except ValueError:
            return "Позиция колонки должна быть числом."

        status = session.get(Status, int(status_id))
        if not status or status.project_id != project.id:
            return "Статус должен принадлежать выбранному проекту."

        if status.id in seen_status_ids:
            return "Один и тот же статус нельзя добавить дважды."
        seen_status_ids.add(status.id)

        if column_id:
            column = session.get(Column, int(column_id))
            if not column or column.project_id != project.id:
                return "Колонка не найдена."
            if any(existing.id != column.id for existing in status.columns):
                return "У статуса уже есть колонка."
            column.status_id = status.id
            column.position = position_value
        else:
            if status.columns:
                return "У статуса уже есть колонка."
            session.add(
                Column(
                    position=position_value,
                    project_id=project.id,
                    status_id=status.id,
                )
            )

    return None
