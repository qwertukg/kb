from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import settings as settings_service
from . import bp


@bp.get("/settings")
def list_settings() -> str:
    settings_values = settings_service.get_settings_values()
    return render_template("settings/list.html", settings=settings_values)


@bp.post("/settings")
def update_settings() -> str:
    values: dict[str, str] = {}
    for key in settings_service.SETTINGS_KEYS:
        values[key] = request.form.get(key, "").strip()
    settings_service.update_settings(values)
    flash("Настройки сохранены.", "success")
    return redirect(url_for("roles.list_settings"))
