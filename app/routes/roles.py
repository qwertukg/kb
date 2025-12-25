from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..services import roles as roles_service
from . import bp


@bp.get("/roles")
def list_roles() -> str:
    roles = roles_service.list_roles()
    return render_template("roles/list.html", roles=roles)


@bp.get("/roles/new")
def new_role() -> str:
    return render_template("roles/form.html", role=None)


@bp.post("/roles")
def create_role() -> str:
    name = request.form.get("name", "").strip()
    instruction = request.form.get("instruction", "").strip() or None

    role, error = roles_service.create_role(name, instruction)
    if error:
        flash(error, "danger")
        return render_template("roles/form.html", role=None, name=name, instruction=instruction)

    flash("Роль создана.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.get("/roles/<int:role_id>/edit")
def edit_role(role_id: int) -> str:
    role = roles_service.get_role(role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    return render_template("roles/form.html", role=role)


@bp.post("/roles/<int:role_id>")
def update_role(role_id: int) -> str:
    name = request.form.get("name", "").strip()
    instruction = request.form.get("instruction", "").strip() or None

    role, error = roles_service.update_role(role_id, name, instruction)
    if error:
        flash(error, "danger")
        role_obj = role or roles_service.get_role(role_id)
        return render_template("roles/form.html", role=role_obj, name=name, instruction=instruction)

    flash("Роль обновлена.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.post("/roles/<int:role_id>/delete")
def delete_role(role_id: int) -> str:
    error = roles_service.delete_role(role_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_roles"))

    flash("Роль удалена.", "success")
    return redirect(url_for("roles.list_roles"))
