from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import settings as settings_service
from . import bp


@bp.get("/settings")
def list_settings() -> str:
    parameters = settings_service.list_parameters()
    return render_template("settings/list.html", parameters=parameters)


@bp.get("/settings/new")
def new_setting() -> str:
    return render_template("settings/form.html", parameter=None)


@bp.post("/settings")
def create_setting() -> str:
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()

    parameter, error = settings_service.create_parameter(key, value)
    if error:
        flash(error, "danger")
        return render_template(
            "settings/form.html",
            parameter=None,
            key=key,
            value=value,
        )

    flash("Параметр создан.", "success")
    return redirect(url_for("roles.list_settings"))


@bp.get("/settings/<int:parameter_id>/edit")
def edit_setting(parameter_id: int) -> str:
    parameter = settings_service.get_parameter(parameter_id)
    if not parameter:
        flash("Параметр не найден.", "danger")
        return redirect(url_for("roles.list_settings"))

    return render_template("settings/form.html", parameter=parameter)


@bp.post("/settings/<int:parameter_id>")
def update_setting(parameter_id: int) -> str:
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()

    parameter, error = settings_service.update_parameter(parameter_id, key, value)
    if error:
        flash(error, "danger")
        parameter_obj = parameter or settings_service.get_parameter(parameter_id)
        return render_template(
            "settings/form.html",
            parameter=parameter_obj,
            key=key,
            value=value,
        )

    flash("Параметр обновлен.", "success")
    return redirect(url_for("roles.list_settings"))


@bp.post("/settings/<int:parameter_id>/delete")
def delete_setting(parameter_id: int) -> str:
    error = settings_service.delete_parameter(parameter_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_settings"))

    flash("Параметр удален.", "success")
    return redirect(url_for("roles.list_settings"))
