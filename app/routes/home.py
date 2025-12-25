from __future__ import annotations

import time

from flask import Response, render_template, request, stream_with_context

from ..services import home as home_service
from . import bp


@bp.get("/")
def index() -> str:
    board_id = request.args.get("board_id", type=int)
    context = home_service.get_home_context(board_id)
    if request.args.get("partial") == "1":
        return render_template("partials/kanban.html", **context)
    return render_template("home.html", **context)


@bp.get("/events")
def events() -> Response:
    @stream_with_context
    def stream():
        while True:
            yield f"data: {time.time()}\n\n"
            time.sleep(2)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
