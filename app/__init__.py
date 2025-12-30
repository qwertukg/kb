from __future__ import annotations

import os

from flasgger import Swagger
from flask import Flask
from sqlalchemy import select

from .db import SessionLocal
from llm import codex as codex_llm
from .models import Project
from .routes import bp
from .api import api_bp
from .socketio import socketio
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
    app.register_blueprint(api_bp)
    Swagger(
        app,
        config={
            "headers": [],
            "swagger_ui_bundle_js": "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            "swagger_ui_standalone_preset_js": "https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js",
            "swagger_ui_css": "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
            "jquery_js": "https://unpkg.com/jquery@3.7.1/dist/jquery.min.js",
            "specs_route": "/api/docs",
            "specs": [
                {
                    "endpoint": "apispec_1",
                    "route": "/api/docs/spec.json",
                    "rule_filter": lambda rule: rule.rule.startswith("/api/"),
                    "model_filter": lambda tag: True,
                }
            ],
        },
        template={
            "swagger": "2.0",
            "info": {"title": "KB Admin API", "version": "1.0.0"},
        },
    )
    socketio.init_app(app)
    codex_llm.write_codex_config(settings_service.get_parameter_value("CONFIG"))
    from .listeners import task_status_listener  # noqa: F401

    @app.context_processor
    def inject_projects() -> dict[str, list[Project]]:
        session = SessionLocal()
        projects = session.execute(select(Project).order_by(Project.name)).scalars().all()
        return {"menu_projects": projects}

    @app.teardown_appcontext
    def shutdown_session(exception: Exception | None = None) -> None:
        SessionLocal.remove()

    return app
