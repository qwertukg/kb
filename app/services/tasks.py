from __future__ import annotations

from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..llm.codex import run_task_prompt
from ..models import Agent, Board, Message, Status, Task
from ..services import settings as settings_service


def _sync_task_assignment(session, task: Task) -> None:
    assigned_agent = (
        session.execute(select(Agent).where(Agent.current_task_id == task.id))
        .scalars()
        .first()
    )
    if assigned_agent and assigned_agent.working_status_id != task.status_id:
        assigned_agent.current_task_id = None
        assigned_agent = None

    if assigned_agent:
        return

    available_agent = (
        session.execute(
            select(Agent)
            .where(
                Agent.working_status_id == task.status_id,
                Agent.current_task_id.is_(None),
            )
            .order_by(Agent.name)
        )
        .scalars()
        .first()
    )
    if available_agent:
        available_agent.current_task_id = task.id
        last_message = (
            session.execute(
                select(Message).where(Message.task_id == task.id).order_by(Message.id.desc())
            )
            .scalars()
            .first()
        )
        if not last_message:
            return

        api_key = settings_service.get_parameter_value("API_KEY")
        model = settings_service.get_parameter_value("MODEL")
        response, is_completed, error_message = run_task_prompt(
            available_agent,
            last_message.text,
            api_key,
            model,
        )
        if error_message:
            _handle_llm_error(session, task, available_agent, error_message)
            return

        if response and is_completed:
            _handle_llm_success(session, task, available_agent, response)
            return

        if response:
            _handle_llm_error(session, task, available_agent, response)
            return


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
    _sync_task_assignment(session, task)
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
    _sync_task_assignment(session, task)
    session.commit()
    return task, None


def delete_task(task_id: int) -> str | None:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        return "Задача не найдена."

    agents = session.execute(select(Agent).where(Agent.current_task_id == task.id)).scalars().all()
    for agent in agents:
        agent.current_task_id = None
    session.delete(task)
    session.commit()
    return None


def _handle_llm_success(session, task: Task, agent: Agent, response: str) -> None:
    session.add(Message(task_id=task.id, author_id=agent.id, text=response))
    if agent.success_status_id:
        task.status_id = agent.success_status_id
    _sync_task_assignment(session, task)


def _handle_llm_error(session, task: Task, agent: Agent, error_message: str) -> None:
    session.add(Message(task_id=task.id, author_id=agent.id, text=error_message))
    if agent.error_status_id:
        task.status_id = agent.error_status_id
    _sync_task_assignment(session, task)


def sent_to_llm(task_id: int) -> tuple[Task | None, str | None]:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        return None, "Задача не найдена."

    last_message = (
        session.execute(
            select(Message).where(Message.task_id == task.id).order_by(Message.id.desc())
        )
        .scalars()
        .first()
    )
    if not last_message:
        return task, "В задаче нет сообщений для отправки."

    agent = (
        session.execute(
            select(Agent)
            .options(selectinload(Agent.role))
            .where(Agent.current_task_id == task.id)
        )
        .scalars()
        .first()
    )
    if not agent:
        return task, "Нет назначенного агента для задачи."

    api_key = settings_service.get_parameter_value("API_KEY")
    model = settings_service.get_parameter_value("MODEL")
    response, is_completed, error_message = run_task_prompt(
        agent,
        last_message.text,
        api_key,
        model,
    )
    if error_message:
        _handle_llm_error(session, task, agent, error_message)
        session.commit()
        return task, error_message

    if response and is_completed:
        _handle_llm_success(session, task, agent, response)
        session.commit()
        return task, None

    if response:
        _handle_llm_error(session, task, agent, response)
        session.commit()
        return task, response

    error_message = "Codex-agent не вернул результат."
    _handle_llm_error(session, task, agent, error_message)
    session.commit()
    return task, error_message
