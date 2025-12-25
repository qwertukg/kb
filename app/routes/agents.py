from __future__ import annotations

from collections import defaultdict

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Agent, Board, Role, Status
from . import bp


def load_agent_form_data(session: SessionLocal):
    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents = defaultdict(list)
    for agent in agents:
        if agent.working_status_id:
            status_agents[agent.working_status_id].append(agent.name)
    return roles, boards, statuses, status_agents


@bp.get("/agents")
def list_agents() -> str:
    session = SessionLocal()
    agents = (
        session.execute(
            select(Agent)
            .options(
                selectinload(Agent.role),
                selectinload(Agent.board),
                selectinload(Agent.success_status),
                selectinload(Agent.error_status),
                selectinload(Agent.working_status),
            )
            .order_by(Agent.name)
        )
        .scalars()
        .all()
    )
    return render_template("agents/list.html", agents=agents)


@bp.get("/agents/new")
def new_agent() -> str:
    session = SessionLocal()
    roles, boards, statuses, status_agents = load_agent_form_data(session)
    return render_template(
        "agents/form.html",
        agent=None,
        roles=roles,
        boards=boards,
        statuses=statuses,
        status_agents=status_agents,
    )


@bp.post("/agents")
def create_agent() -> str:
    name = request.form.get("name", "").strip()
    role_id = request.form.get("role_id", "").strip()
    board_id = request.form.get("board_id", "").strip()
    success_status_id = request.form.get("success_status_id", "").strip()
    error_status_id = request.form.get("error_status_id", "").strip()
    working_status_id = request.form.get("working_status_id", "").strip()
    acceptance_criteria = request.form.get("acceptance_criteria", "").strip() or None
    transfer_criteria = request.form.get("transfer_criteria", "").strip() or None

    session = SessionLocal()
    roles, boards, statuses, status_agents = load_agent_form_data(session)

    if (
        not name
        or not role_id
        or not board_id
        or not success_status_id
        or not error_status_id
        or not working_status_id
    ):
        flash("Имя, роль, доска и статусы обязательны.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    role = session.get(Role, int(role_id))
    if not role:
        flash("Роль не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    success_status = session.get(Status, int(success_status_id))
    error_status = session.get(Status, int(error_status_id))
    working_status = session.get(Status, int(working_status_id))
    if (
        not success_status
        or not error_status
        or not working_status
        or success_status.board_id != board.id
        or error_status.board_id != board.id
        or working_status.board_id != board.id
    ):
        flash("Статусы должны принадлежать выбранной доске.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    agent = Agent(
        name=name,
        role_id=role.id,
        board_id=board.id,
        success_status_id=success_status.id,
        error_status_id=error_status.id,
        working_status_id=working_status.id,
        acceptance_criteria=acceptance_criteria,
        transfer_criteria=transfer_criteria,
    )
    session.add(agent)
    session.commit()
    flash("Агент создан.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.get("/agents/<int:agent_id>/edit")
def edit_agent(agent_id: int) -> str:
    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    roles, boards, statuses, status_agents = load_agent_form_data(session)
    return render_template(
        "agents/form.html",
        agent=agent,
        roles=roles,
        boards=boards,
        statuses=statuses,
        status_agents=status_agents,
    )


@bp.post("/agents/<int:agent_id>")
def update_agent(agent_id: int) -> str:
    name = request.form.get("name", "").strip()
    role_id = request.form.get("role_id", "").strip()
    board_id = request.form.get("board_id", "").strip()
    success_status_id = request.form.get("success_status_id", "").strip()
    error_status_id = request.form.get("error_status_id", "").strip()
    working_status_id = request.form.get("working_status_id", "").strip()
    acceptance_criteria = request.form.get("acceptance_criteria", "").strip() or None
    transfer_criteria = request.form.get("transfer_criteria", "").strip() or None

    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    roles, boards, statuses, status_agents = load_agent_form_data(session)

    if (
        not name
        or not role_id
        or not board_id
        or not success_status_id
        or not error_status_id
        or not working_status_id
    ):
        flash("Имя, роль, доска и статусы обязательны.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    role = session.get(Role, int(role_id))
    if not role:
        flash("Роль не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    success_status = session.get(Status, int(success_status_id))
    error_status = session.get(Status, int(error_status_id))
    working_status = session.get(Status, int(working_status_id))
    if (
        not success_status
        or not error_status
        or not working_status
        or success_status.board_id != board.id
        or error_status.board_id != board.id
        or working_status.board_id != board.id
    ):
        flash("Статусы должны принадлежать выбранной доске.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    agent.name = name
    agent.role_id = role.id
    agent.board_id = board.id
    agent.success_status_id = success_status.id
    agent.error_status_id = error_status.id
    agent.working_status_id = working_status.id
    agent.acceptance_criteria = acceptance_criteria
    agent.transfer_criteria = transfer_criteria
    session.commit()
    flash("Агент обновлен.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.post("/agents/<int:agent_id>/delete")
def delete_agent(agent_id: int) -> str:
    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    session.delete(agent)
    session.commit()
    flash("Агент удален.", "success")
    return redirect(url_for("roles.list_agents"))
