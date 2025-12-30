from __future__ import annotations

from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from . import agents, parameters, projects, roles, settings, statuses, tasks  # noqa: E402,F401
