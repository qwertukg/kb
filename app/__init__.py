from __future__ import annotations

import os

from flask import Flask
from sqlalchemy import select

from .db import SessionLocal
from .llm import codex as codex_llm
from .models import Board
from .routes import bp
from .services import settings as settings_service


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
    trusted_hosts = os.getenv("TRUSTED_HOSTS")
    if trusted_hosts:
        app.config["TRUSTED_HOSTS"] = [host.strip() for host in trusted_hosts.split(",") if host.strip()]
    else:
        app.config["TRUSTED_HOSTS"] = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]

    app.register_blueprint(bp)
    codex_llm.write_codex_config(settings_service.get_parameter_value("CONFIG"))

    @app.context_processor
    def inject_boards() -> dict[str, list[Board]]:
        session = SessionLocal()
        boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
        return {"menu_boards": boards}

    @app.teardown_appcontext
    def shutdown_session(exception: Exception | None = None) -> None:
        SessionLocal.remove()

    return app
