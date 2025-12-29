from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from ..services import agents as agents_service
from . import bp


@bp.get("/agents")
def list_agents() -> str:
    agents = agents_service.list_agents()
    return render_template("agents/list.html", agents=agents)


@bp.get("/agents/new")
def new_agent() -> str:
    roles, projects, statuses, status_agents = agents_service.get_form_data()
    return render_template(
        "agents/form.html",
        agent=None,
        roles=roles,
        projects=projects,
        statuses=statuses,
        status_agents=status_agents,
    )


@bp.post("/agents")
def create_agent() -> str:
    name = request.form.get("name", "").strip()
    role_id = request.form.get("role_id", "").strip()
    project_id = request.form.get("project_id", "").strip()
    success_status_id = request.form.get("success_status_id", "").strip()
    error_status_id = request.form.get("error_status_id", "").strip()
    working_status_id = request.form.get("working_status_id", "").strip()
    acceptance_criteria = request.form.get("acceptance_criteria", "").strip() or None
    transfer_criteria = request.form.get("transfer_criteria", "").strip() or None

    agent, error = agents_service.create_agent(
        name,
        role_id,
        project_id,
        success_status_id,
        error_status_id,
        working_status_id,
        acceptance_criteria,
        transfer_criteria,
    )
    if error:
        roles, projects, statuses, status_agents = agents_service.get_form_data()
        flash(error, "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            projects=projects,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            project_id=project_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    flash("Агент создан.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.get("/agents/<int:agent_id>/edit")
def edit_agent(agent_id: int) -> str:
    agent = agents_service.get_agent(agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    roles, projects, statuses, status_agents = agents_service.get_form_data()
    return render_template(
        "agents/form.html",
        agent=agent,
        roles=roles,
        projects=projects,
        statuses=statuses,
        status_agents=status_agents,
    )


@bp.post("/agents/<int:agent_id>")
def update_agent(agent_id: int) -> str:
    name = request.form.get("name", "").strip()
    role_id = request.form.get("role_id", "").strip()
    project_id = request.form.get("project_id", "").strip()
    success_status_id = request.form.get("success_status_id", "").strip()
    error_status_id = request.form.get("error_status_id", "").strip()
    working_status_id = request.form.get("working_status_id", "").strip()
    acceptance_criteria = request.form.get("acceptance_criteria", "").strip() or None
    transfer_criteria = request.form.get("transfer_criteria", "").strip() or None

    agent, error = agents_service.update_agent(
        agent_id,
        name,
        role_id,
        project_id,
        success_status_id,
        error_status_id,
        working_status_id,
        acceptance_criteria,
        transfer_criteria,
    )
    if error:
        roles, projects, statuses, status_agents = agents_service.get_form_data()
        agent_obj = agent or agents_service.get_agent(agent_id)
        flash(error, "danger")
        return render_template(
            "agents/form.html",
            agent=agent_obj,
            roles=roles,
            projects=projects,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            project_id=project_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    flash("Агент обновлен.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.post("/agents/<int:agent_id>/delete")
def delete_agent(agent_id: int) -> str:
    error = agents_service.delete_agent(agent_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_agents"))

    flash("Агент удален.", "success")
    return redirect(url_for("roles.list_agents"))
