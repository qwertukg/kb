from __future__ import annotations

from flask import Blueprint

bp = Blueprint("roles", __name__)

from . import agents, boards, home, roles, statuses, tasks  # noqa: F401, E402
