from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from llm.codex import register_codex_agent, remove_codex_agent
from ..models import Agent, Project, Role, Status
from ..services import settings as settings_service


def list_agents() -> list[Agent]:
    session = SessionLocal()
    return (
        session.execute(
            select(Agent)
            .options(
                selectinload(Agent.role),
                selectinload(Agent.project),
                selectinload(Agent.current_task),
                selectinload(Agent.success_status),
                selectinload(Agent.error_status),
                selectinload(Agent.working_status),
            )
            .order_by(Agent.name)
        )
        .scalars()
        .all()
    )


def get_agent(agent_id: int) -> Agent | None:
    session = SessionLocal()
    return session.get(Agent, agent_id)


def get_form_data() -> tuple[list[Role], list[Project], list[Status], dict[int, list[str]]]:
    session = SessionLocal()
    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    projects = session.execute(select(Project).order_by(Project.name)).scalars().all()
    statuses = session.execute(
        select(Status)
        .options(selectinload(Status.project))
        .order_by(Status.project_id, Status.name)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents: dict[int, list[str]] = defaultdict(list)
    for agent in agents:
        if agent.working_status_id:
            status_agents[agent.working_status_id].append(agent.name)
    return roles, projects, statuses, status_agents


def create_agent(
    name: str,
    role_id: str,
    project_id: str,
    success_status_id: str,
    error_status_id: str,
    working_status_id: str,
    acceptance_criteria: str | None,
    transfer_criteria: str | None,
) -> tuple[Agent | None, str | None]:
    if (
        not name
        or not role_id
        or not project_id
        or not success_status_id
        or not error_status_id
        or not working_status_id
    ):
        return None, "Имя, роль, проект и статусы обязательны."

    session = SessionLocal()
    role = session.get(Role, int(role_id))
    if not role:
        return None, "Роль не найдена."

    project = session.get(Project, int(project_id))
    if not project:
        return None, "Проект не найден."

    success_status = session.get(Status, int(success_status_id))
    error_status = session.get(Status, int(error_status_id))
    working_status = session.get(Status, int(working_status_id))
    if (
        not success_status
        or not error_status
        or not working_status
        or success_status.project_id != project.id
        or error_status.project_id != project.id
        or working_status.project_id != project.id
    ):
        return None, "Статусы должны принадлежать выбранному проекту."

    agent = Agent(
        name=name,
        role_id=role.id,
        project_id=project.id,
        success_status_id=success_status.id,
        error_status_id=error_status.id,
        working_status_id=working_status.id,
        acceptance_criteria=acceptance_criteria,
        transfer_criteria=transfer_criteria,
    )
    session.add(agent)
    session.commit()
    settings = settings_service.get_settings()
    register_codex_agent(agent, settings.api_key, settings.model)
    return agent, None


def update_agent(
    agent_id: int,
    name: str,
    role_id: str,
    project_id: str,
    success_status_id: str,
    error_status_id: str,
    working_status_id: str,
    acceptance_criteria: str | None,
    transfer_criteria: str | None,
) -> tuple[Agent | None, str | None]:
    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        return None, "Агент не найден."

    if (
        not name
        or not role_id
        or not project_id
        or not success_status_id
        or not error_status_id
        or not working_status_id
    ):
        return None, "Имя, роль, проект и статусы обязательны."

    role = session.get(Role, int(role_id))
    if not role:
        return None, "Роль не найдена."

    project = session.get(Project, int(project_id))
    if not project:
        return None, "Проект не найден."

    success_status = session.get(Status, int(success_status_id))
    error_status = session.get(Status, int(error_status_id))
    working_status = session.get(Status, int(working_status_id))
    if (
        not success_status
        or not error_status
        or not working_status
        or success_status.project_id != project.id
        or error_status.project_id != project.id
        or working_status.project_id != project.id
    ):
        return None, "Статусы должны принадлежать выбранному проекту."

    previous_working_status_id = agent.working_status_id
    agent.name = name
    agent.role_id = role.id
    agent.project_id = project.id
    agent.success_status_id = success_status.id
    agent.error_status_id = error_status.id
    agent.working_status_id = working_status.id
    agent.acceptance_criteria = acceptance_criteria
    agent.transfer_criteria = transfer_criteria
    if agent.current_task_id and previous_working_status_id != working_status.id:
        agent.current_task_id = None
    session.commit()
    settings = settings_service.get_settings()
    register_codex_agent(agent, settings.api_key, settings.model)
    return agent, None


def delete_agent(agent_id: int) -> str | None:
    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        return "Агент не найден."

    remove_codex_agent(agent.id)
    session.delete(agent)
    session.commit()
    return None
