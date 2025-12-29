from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import statuses as statuses_service
from . import bp


@bp.get("/statuses")
def list_statuses() -> str:
    statuses = statuses_service.list_statuses()
    return render_template("statuses/list.html", statuses=statuses)


@bp.get("/statuses/new")
def new_status() -> str:
    projects = statuses_service.get_form_projects()
    return render_template("statuses/form.html", status=None, projects=projects)


@bp.post("/statuses")
def create_status() -> str:
    name = request.form.get("name", "").strip()
    color = request.form.get("color", "").strip()
    project_id = request.form.get("project_id", "").strip()

    status, error = statuses_service.create_status(name, color, project_id)
    if error:
        projects = statuses_service.get_form_projects()
        flash(error, "danger")
        return render_template(
            "statuses/form.html",
            status=None,
            projects=projects,
            name=name,
            color=color,
            project_id=project_id,
        )

    flash("Статус создан.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.get("/statuses/<int:status_id>/edit")
def edit_status(status_id: int) -> str:
    status = statuses_service.get_status(status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    projects = statuses_service.get_form_projects()
    return render_template("statuses/form.html", status=status, projects=projects)


@bp.post("/statuses/<int:status_id>")
def update_status(status_id: int) -> str:
    name = request.form.get("name", "").strip()
    color = request.form.get("color", "").strip()
    project_id = request.form.get("project_id", "").strip()

    status, error = statuses_service.update_status(status_id, name, color, project_id)
    if error:
        projects = statuses_service.get_form_projects()
        status_obj = status or statuses_service.get_status(status_id)
        flash(error, "danger")
        return render_template(
            "statuses/form.html",
            status=status_obj,
            projects=projects,
            name=name,
            color=color,
            project_id=project_id,
        )

    flash("Статус обновлен.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.post("/statuses/<int:status_id>/delete")
def delete_status(status_id: int) -> str:
    error = statuses_service.delete_status(status_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_statuses"))

    flash("Статус удален.", "success")
    return redirect(url_for("roles.list_statuses"))
