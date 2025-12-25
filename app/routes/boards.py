from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Board
from . import bp


@bp.get("/boards")
def list_boards() -> str:
    session = SessionLocal()
    boards = (
        session.execute(select(Board).options(selectinload(Board.statuses)).order_by(Board.name))
        .scalars()
        .all()
    )
    return render_template("boards/list.html", boards=boards)


@bp.get("/boards/new")
def new_board() -> str:
    return render_template("boards/form.html", board=None)


@bp.post("/boards")
def create_board() -> str:
    name = request.form.get("name", "").strip()

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("boards/form.html", board=None, name=name)

    session = SessionLocal()
    exists = session.execute(select(Board).where(Board.name == name)).scalar_one_or_none()
    if exists:
        flash("Доска с таким именем уже существует.", "danger")
        return render_template("boards/form.html", board=None, name=name)

    board = Board(name=name)
    session.add(board)
    session.commit()
    flash("Доска создана.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.get("/boards/<int:board_id>/edit")
def edit_board(board_id: int) -> str:
    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    return render_template("boards/form.html", board=board)


@bp.post("/boards/<int:board_id>")
def update_board(board_id: int) -> str:
    name = request.form.get("name", "").strip()

    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("boards/form.html", board=board, name=name)

    exists = (
        session.execute(select(Board).where(Board.name == name, Board.id != board_id))
        .scalar_one_or_none()
    )
    if exists:
        flash("Доска с таким именем уже существует.", "danger")
        return render_template("boards/form.html", board=board, name=name)

    board.name = name
    session.commit()
    flash("Доска обновлена.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.post("/boards/<int:board_id>/delete")
def delete_board(board_id: int) -> str:
    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    session.delete(board)
    session.commit()
    flash("Доска удалена.", "success")
    return redirect(url_for("roles.list_boards"))
