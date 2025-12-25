from __future__ import annotations

from flask import render_template, request

from ..services import home as home_service
from . import bp


@bp.get("/")
def index() -> str:
    board_id = request.args.get("board_id", type=int)
    context = home_service.get_home_context(board_id)
    return render_template("home.html", **context)
