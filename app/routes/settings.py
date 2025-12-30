from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import settings as settings_service
from . import bp


@bp.get("/settings")
def list_settings() -> str:
    settings = settings_service.get_settings()
    return render_template("settings/list.html", settings=settings)


@bp.post("/settings")
def update_settings() -> str:
    settings_service.update_settings(
        request.form.get("api_key", "").strip(),
        request.form.get("model", "").strip(),
        request.form.get("instructions", "").strip(),
        request.form.get("config", "").strip(),
    )
    flash("Настройки сохранены.", "success")
    return redirect(url_for("roles.list_settings"))
