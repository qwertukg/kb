from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from ..db import SessionLocal
from ..models import Role
from . import bp


@bp.get("/roles")
def list_roles() -> str:
    session = SessionLocal()
    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    return render_template("roles/list.html", roles=roles)


@bp.get("/roles/new")
def new_role() -> str:
    return render_template("roles/form.html", role=None)


@bp.post("/roles")
def create_role() -> str:
    name = request.form.get("name", "").strip()
    instruction = request.form.get("instruction", "").strip() or None

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("roles/form.html", role=None, name=name, instruction=instruction)

    session = SessionLocal()
    exists = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if exists:
        flash("Роль с таким именем уже существует.", "danger")
        return render_template("roles/form.html", role=None, name=name, instruction=instruction)

    role = Role(name=name, instruction=instruction)
    session.add(role)
    session.commit()
    flash("Роль создана.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.get("/roles/<int:role_id>/edit")
def edit_role(role_id: int) -> str:
    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    return render_template("roles/form.html", role=role)


@bp.post("/roles/<int:role_id>")
def update_role(role_id: int) -> str:
    name = request.form.get("name", "").strip()
    instruction = request.form.get("instruction", "").strip() or None

    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("roles/form.html", role=role, name=name, instruction=instruction)

    exists = (
        session.execute(select(Role).where(Role.name == name, Role.id != role_id))
        .scalar_one_or_none()
    )
    if exists:
        flash("Роль с таким именем уже существует.", "danger")
        return render_template("roles/form.html", role=role, name=name, instruction=instruction)

    role.name = name
    role.instruction = instruction
    session.commit()
    flash("Роль обновлена.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.post("/roles/<int:role_id>/delete")
def delete_role(role_id: int) -> str:
    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    session.delete(role)
    session.commit()
    flash("Роль удалена.", "success")
    return redirect(url_for("roles.list_roles"))
