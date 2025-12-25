from __future__ import annotations

from flask import render_template, request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Agent, Board, Status, Task
from . import bp


@bp.get("/")
def index() -> str:
    session = SessionLocal()
    board_id = request.args.get("board_id", type=int)
    current_board_name = None
    statuses = (
        session.execute(
            select(Status)
            .options(selectinload(Status.working_agents), selectinload(Status.board))
            .order_by(Status.board_id, Status.position)
        )
        .scalars()
        .all()
    )
    if board_id:
        statuses = [status for status in statuses if status.board_id == board_id]
        board = session.get(Board, board_id)
        current_board_name = board.name if board else None
    task_query = select(Task).options(selectinload(Task.messages)).order_by(Task.id)
    if board_id:
        task_query = task_query.where(Task.board_id == board_id)
    tasks = session.execute(task_query).scalars().all()

    tasks_by_status: dict[int, list[tuple[Task, Agent | None]]] = {}
    free_agents_by_status: dict[int, list[Agent]] = {}
    statuses_by_board: dict[int, list[Status]] = {}
    for status in statuses:
        agents = sorted(status.working_agents, key=lambda agent: agent.name.lower())
        status_tasks = [task for task in tasks if task.status_id == status.id]
        assigned: list[tuple[Task, Agent | None]] = []
        free_agents = agents.copy()
        for task in status_tasks:
            agent = free_agents.pop(0) if free_agents else None
            assigned.append((task, agent))
        tasks_by_status[status.id] = assigned
        free_agents_by_status[status.id] = free_agents
        statuses_by_board.setdefault(status.board_id, []).append(status)

    return render_template(
        "home.html",
        statuses_by_board=statuses_by_board,
        tasks_by_status=tasks_by_status,
        free_agents_by_status=free_agents_by_status,
        current_board_name=current_board_name,
    )
