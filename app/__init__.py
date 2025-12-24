from __future__ import annotations

import os

from flask import Flask

from .db import SessionLocal
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

    app.register_blueprint(bp)

    @app.teardown_appcontext
    def shutdown_session(exception: Exception | None = None) -> None:
        SessionLocal.remove()

    return app
