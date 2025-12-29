from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import projects as projects_service
from . import bp


def _collect_board_rows() -> list[dict[str, str]]:
    column_ids = request.form.getlist("column_id")
    status_ids = request.form.getlist("status_id")
    positions = request.form.getlist("position")
    deleted_flags = request.form.getlist("is_deleted")

    rows: list[dict[str, str]] = []
    for index in range(len(status_ids)):
        rows.append(
            {
                "column_id": column_ids[index] if index < len(column_ids) else "",
                "status_id": status_ids[index],
                "position": positions[index] if index < len(positions) else "",
                "is_deleted": deleted_flags[index] if index < len(deleted_flags) else "",
            }
        )
    return rows


@bp.get("/projects")
def list_projects() -> str:
    projects = projects_service.list_projects()
    return render_template("projects/list.html", projects=projects)


@bp.get("/projects/new")
def new_project() -> str:
    return render_template("projects/form.html", project=None, statuses=[])


@bp.post("/projects")
def create_project() -> str:
    name = request.form.get("name", "").strip()
    board_rows = _collect_board_rows()

    project, error = projects_service.create_project(name, board_rows)
    if error:
        flash(error, "danger")
        return render_template(
            "projects/form.html",
            project=None,
            name=name,
            board_rows=board_rows,
            statuses=[],
        )

    flash("Проект создан.", "success")
    return redirect(url_for("roles.list_projects"))


@bp.get("/projects/<int:project_id>/edit")
def edit_project(project_id: int) -> str:
    project = projects_service.get_project_with_board(project_id)
    if not project:
        flash("Проект не найден.", "danger")
        return redirect(url_for("roles.list_projects"))

    statuses = projects_service.get_project_statuses(project_id)
    return render_template("projects/form.html", project=project, statuses=statuses)


@bp.post("/projects/<int:project_id>")
def update_project(project_id: int) -> str:
    name = request.form.get("name", "").strip()
    board_rows = _collect_board_rows()

    project, error = projects_service.update_project(project_id, name, board_rows)
    if error:
        flash(error, "danger")
        project_obj = project or projects_service.get_project_with_board(project_id)
        statuses = projects_service.get_project_statuses(project_id)
        return render_template(
            "projects/form.html",
            project=project_obj,
            name=name,
            board_rows=board_rows,
            statuses=statuses,
        )

    flash("Проект обновлен.", "success")
    return redirect(url_for("roles.list_projects"))


@bp.post("/projects/<int:project_id>/delete")
def delete_project(project_id: int) -> str:
    error = projects_service.delete_project(project_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_projects"))

    flash("Проект удален.", "success")
    return redirect(url_for("roles.list_projects"))
