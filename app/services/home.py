from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Agent, Column, Project, Status, Task


def get_home_context(project_id: int | None) -> dict[str, object]:
    session = SessionLocal()
    current_project_name = None
    columns = (
        session.execute(
            select(Column)
            .options(
                selectinload(Column.project),
                selectinload(Column.status).selectinload(Status.project),
                selectinload(Column.status).selectinload(Status.working_agents),
            )
            .order_by(Column.project_id, Column.position)
        )
        .scalars()
        .all()
    )
    if project_id:
        columns = [column for column in columns if column.project_id == project_id]
        project = session.get(Project, project_id)
        current_project_name = project.name if project else None

    task_query = select(Task).options(selectinload(Task.messages)).order_by(Task.id)
    if project_id:
        task_query = task_query.where(Task.project_id == project_id)
    tasks = session.execute(task_query).scalars().all()

    tasks_by_status: dict[int, list[tuple[Task, Agent | None]]] = {}
    free_agents_by_status: dict[int, list[Agent]] = {}
    statuses_by_project: dict[int, list[Status]] = {}
    for column in columns:
        status = column.status
        if not status:
            continue
        agents = sorted(status.working_agents, key=lambda agent: agent.name.lower())
        status_tasks = [task for task in tasks if task.status_id == status.id]
        assigned: list[tuple[Task, Agent | None]] = []
        free_agents = agents.copy()
        for task in status_tasks:
            agent = free_agents.pop(0) if free_agents else None
            assigned.append((task, agent))
        tasks_by_status[status.id] = assigned
        free_agents_by_status[status.id] = free_agents
        statuses_by_project.setdefault(status.project_id, []).append(status)

    return {
        "statuses_by_project": statuses_by_project,
        "tasks_by_status": tasks_by_status,
        "free_agents_by_status": free_agents_by_status,
        "current_project_name": current_project_name,
    }
