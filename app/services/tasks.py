from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Agent, Board, Message, Status, Task


def list_tasks() -> list[Task]:
    session = SessionLocal()
    return (
        session.execute(
            select(Task)
            .options(
                selectinload(Task.board),
                selectinload(Task.status),
                selectinload(Task.messages).selectinload(Message.author),
            )
            .order_by(Task.id)
        )
        .scalars()
        .all()
    )


def get_task(task_id: int) -> Task | None:
    session = SessionLocal()
    return session.get(Task, task_id)


def get_form_data() -> tuple[list[Board], list[Status], list[Agent], dict[int, list[str]]]:
    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents: dict[int, list[str]] = defaultdict(list)
    for agent in agents:
        if agent.working_status_id:
            status_agents[agent.working_status_id].append(agent.name)
    return boards, statuses, agents, status_agents


def create_task(
    title: str,
    board_id: str,
    status_id: str,
    author_id: str,
    message_text: str,
) -> tuple[Task | None, str | None]:
    if not title or not board_id or not status_id or not author_id or not message_text:
        return None, "Заголовок, доска, статус, автор и сообщение обязательны."

    session = SessionLocal()
    board = session.get(Board, int(board_id))
    status = session.get(Status, int(status_id))
    author = session.get(Agent, int(author_id)) if author_id else None
    if not board or not status or status.board_id != board.id or not author:
        return None, "Проверьте доску, статус и автора."

    task = Task(title=title, board_id=board.id, status_id=status.id)
    session.add(task)
    session.flush()
    session.add(Message(task_id=task.id, author_id=author.id, text=message_text))
    session.commit()
    return task, None


def update_task(
    task_id: int,
    title: str,
    board_id: str,
    status_id: str,
    author_id: str,
    message_text: str,
) -> tuple[Task | None, str | None]:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        return None, "Задача не найдена."

    if not title or not board_id or not status_id:
        return None, "Заголовок, доска и статус обязательны."

    board = session.get(Board, int(board_id))
    status = session.get(Status, int(status_id))
    author = session.get(Agent, int(author_id)) if author_id else None
    if not board or not status or status.board_id != board.id:
        return None, "Статус должен принадлежать выбранной доске."
    if message_text and not author:
        return None, "Выберите автора для сообщения."

    task.title = title
    task.board_id = board.id
    task.status_id = status.id
    if message_text:
        session.add(Message(task_id=task.id, author_id=author.id, text=message_text))
    session.commit()
    return task, None


def delete_task(task_id: int) -> str | None:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        return "Задача не найдена."

    session.delete(task)
    session.commit()
    return None
