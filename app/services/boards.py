from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Board


def list_boards() -> list[Board]:
    session = SessionLocal()
    return (
        session.execute(select(Board).options(selectinload(Board.statuses)).order_by(Board.name))
        .scalars()
        .all()
    )


def get_board(board_id: int) -> Board | None:
    session = SessionLocal()
    return session.get(Board, board_id)


def create_board(name: str) -> tuple[Board | None, str | None]:
    if not name:
        return None, "Имя обязательно."

    session = SessionLocal()
    exists = session.execute(select(Board).where(Board.name == name)).scalar_one_or_none()
    if exists:
        return None, "Доска с таким именем уже существует."

    board = Board(name=name)
    session.add(board)
    session.commit()
    return board, None


def update_board(board_id: int, name: str) -> tuple[Board | None, str | None]:
    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        return None, "Доска не найдена."

    if not name:
        return None, "Имя обязательно."

    exists = (
        session.execute(select(Board).where(Board.name == name, Board.id != board_id))
        .scalar_one_or_none()
    )
    if exists:
        return None, "Доска с таким именем уже существует."

    board.name = name
    session.commit()
    return board, None


def delete_board(board_id: int) -> str | None:
    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        return "Доска не найдена."

    session.delete(board)
    session.commit()
    return None
