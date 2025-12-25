from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import boards as boards_service
from . import bp


@bp.get("/boards")
def list_boards() -> str:
    boards = boards_service.list_boards()
    return render_template("boards/list.html", boards=boards)


@bp.get("/boards/new")
def new_board() -> str:
    return render_template("boards/form.html", board=None)


@bp.post("/boards")
def create_board() -> str:
    name = request.form.get("name", "").strip()

    board, error = boards_service.create_board(name)
    if error:
        flash(error, "danger")
        return render_template("boards/form.html", board=None, name=name)

    flash("Доска создана.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.get("/boards/<int:board_id>/edit")
def edit_board(board_id: int) -> str:
    board = boards_service.get_board(board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    return render_template("boards/form.html", board=board)


@bp.post("/boards/<int:board_id>")
def update_board(board_id: int) -> str:
    name = request.form.get("name", "").strip()

    board, error = boards_service.update_board(board_id, name)
    if error:
        flash(error, "danger")
        board_obj = board or boards_service.get_board(board_id)
        return render_template("boards/form.html", board=board_obj, name=name)

    flash("Доска обновлена.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.post("/boards/<int:board_id>/delete")
def delete_board(board_id: int) -> str:
    error = boards_service.delete_board(board_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_boards"))

    flash("Доска удалена.", "success")
    return redirect(url_for("roles.list_boards"))
