from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Board, Status


def list_statuses() -> list[Status]:
    session = SessionLocal()
    return (
        session.execute(select(Status).options(selectinload(Status.board)).order_by(Status.position))
        .scalars()
        .all()
    )


def get_status(status_id: int) -> Status | None:
    session = SessionLocal()
    return session.get(Status, status_id)


def get_form_boards() -> list[Board]:
    session = SessionLocal()
    return session.execute(select(Board).order_by(Board.name)).scalars().all()


def create_status(
    name: str,
    position: str,
    color: str,
    board_id: str,
) -> tuple[Status | None, str | None]:
    if not name or not position or not board_id:
        return None, "Имя, позиция и доска обязательны."

    session = SessionLocal()
    board = session.get(Board, int(board_id))
    if not board:
        return None, "Доска не найдена."

    status = Status(
        name=name,
        position=int(position),
        color=color or "#0d6efd",
        board_id=board.id,
    )
    session.add(status)
    session.commit()
    return status, None


def update_status(
    status_id: int,
    name: str,
    position: str,
    color: str,
    board_id: str,
) -> tuple[Status | None, str | None]:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        return None, "Статус не найден."

    if not name or not position or not board_id:
        return None, "Имя, позиция и доска обязательны."

    board = session.get(Board, int(board_id))
    if not board:
        return None, "Доска не найдена."

    status.name = name
    status.position = int(position)
    status.color = color or "#0d6efd"
    status.board_id = board.id
    session.commit()
    return status, None


def delete_status(status_id: int) -> str | None:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        return "Статус не найден."

    session.delete(status)
    session.commit()
    return None
