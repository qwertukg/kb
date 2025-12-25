from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Board, Status
from . import bp


@bp.get("/statuses")
def list_statuses() -> str:
    session = SessionLocal()
    statuses = (
        session.execute(select(Status).options(selectinload(Status.board)).order_by(Status.position))
        .scalars()
        .all()
    )
    return render_template("statuses/list.html", statuses=statuses)


@bp.get("/statuses/new")
def new_status() -> str:
    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    return render_template("statuses/form.html", status=None, boards=boards)


@bp.post("/statuses")
def create_status() -> str:
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    color = request.form.get("color", "").strip()
    board_id = request.form.get("board_id", "").strip()

    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()

    if not name or not position or not board_id:
        flash("Имя, позиция и доска обязательны.", "danger")
        return render_template(
            "statuses/form.html",
            status=None,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "statuses/form.html",
            status=None,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    status = Status(
        name=name,
        position=int(position),
        color=color or "#0d6efd",
        board_id=board.id,
    )
    session.add(status)
    session.commit()
    flash("Статус создан.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.get("/statuses/<int:status_id>/edit")
def edit_status(status_id: int) -> str:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    return render_template("statuses/form.html", status=status, boards=boards)


@bp.post("/statuses/<int:status_id>")
def update_status(status_id: int) -> str:
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    color = request.form.get("color", "").strip()
    board_id = request.form.get("board_id", "").strip()

    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()

    if not name or not position or not board_id:
        flash("Имя, позиция и доска обязательны.", "danger")
        return render_template(
            "statuses/form.html",
            status=status,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "statuses/form.html",
            status=status,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    status.name = name
    status.position = int(position)
    status.color = color or "#0d6efd"
    status.board_id = board.id
    session.commit()
    flash("Статус обновлен.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.post("/statuses/<int:status_id>/delete")
def delete_status(status_id: int) -> str:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    session.delete(status)
    session.commit()
    flash("Статус удален.", "success")
    return redirect(url_for("roles.list_statuses"))
