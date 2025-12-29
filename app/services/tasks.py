from __future__ import annotations

from collections import defaultdict
from threading import Lock
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from llm.codex import run_task_prompt
from app.socketio import socketio
from ..models import Agent, Message, Parameter, Project, Status, Task

_RUNNING_TASK_IDS: set[int] = set()
_RUNNING_TASK_IDS_LOCK = Lock()


def _set_task_running(task_id: int, is_running: bool) -> None:
    with _RUNNING_TASK_IDS_LOCK:
        if is_running:
            _RUNNING_TASK_IDS.add(task_id)
        else:
            _RUNNING_TASK_IDS.discard(task_id)


def get_running_task_ids() -> set[int]:
    with _RUNNING_TASK_IDS_LOCK:
        return set(_RUNNING_TASK_IDS)


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
        return


def list_tasks() -> list[Task]:
    session = SessionLocal()
    return (
        session.execute(
            select(Task)
            .options(
                selectinload(Task.project),
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


def get_task_with_messages(task_id: int) -> Task | None:
    session = SessionLocal()
    return (
        session.execute(
            select(Task)
            .options(
                selectinload(Task.messages).selectinload(Message.author),
                selectinload(Task.status),
            )
            .where(Task.id == task_id)
        )
        .scalars()
        .first()
    )


def get_task_assigned_agent(task_id: int) -> Agent | None:
    session = SessionLocal()
    return (
        session.execute(
            select(Agent).where(Agent.current_task_id == task_id).order_by(Agent.id)
        )
        .scalars()
        .first()
    )


def update_task_status(task_id: int, status_id: str) -> tuple[Task | None, str | None]:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        return None, "Задача не найдена."

    if not status_id:
        return None, "Статус обязателен."

    status = session.get(Status, int(status_id))
    if not status or status.project_id != task.project_id:
        return None, "Статус должен принадлежать проекту задачи."

    if task.status_id == status.id:
        return task, None

    task.status_id = status.id
    _sync_task_assignment(session, task)
    session.commit()
    return task, None


def get_form_data() -> tuple[list[Project], list[Status], list[Agent], dict[int, list[str]]]:
    session = SessionLocal()
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
    return projects, statuses, agents, status_agents


def create_task(
    title: str,
    project_id: str,
    status_id: str,
    author_id: str,
    message_text: str,
) -> tuple[Task | None, str | None]:
    if not title or not project_id or not status_id or not author_id or not message_text:
        return None, "Заголовок, проект, статус, автор и сообщение обязательны."

    session = SessionLocal()
    project = session.get(Project, int(project_id))
    status = session.get(Status, int(status_id))
    author = session.get(Agent, int(author_id)) if author_id else None
    if not project or not status or status.project_id != project.id or not author:
        return None, "Проверьте проект, статус и автора."

    task = Task(title=title, project_id=project.id, status_id=status.id)
    session.add(task)
    session.flush()
    _sync_task_assignment(session, task)
    session.add(Message(task_id=task.id, author_id=author.id, text=message_text))
    session.commit()
    return task, None


def update_task(
    task_id: int,
    title: str,
    project_id: str,
    status_id: str,
    author_id: str,
    message_text: str,
) -> tuple[Task | None, str | None]:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        return None, "Задача не найдена."

    if not title or not project_id or not status_id:
        return None, "Заголовок, проект и статус обязательны."

    project = session.get(Project, int(project_id))
    status = session.get(Status, int(status_id))
    author = session.get(Agent, int(author_id)) if author_id else None
    if not project or not status or status.project_id != project.id:
        return None, "Статус должен принадлежать выбранному проекту."
    if message_text and not author:
        return None, "Выберите автора для сообщения."

    task.title = title
    task.project_id = project.id
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
    session = SessionLocal.session_factory()
    task = session.get(Task, task_id)
    if not task:
        return None, "Задача не найдена."

    _set_task_running(task_id, True)
    socketio.emit("task_llm_started", {"task_id": task_id})

    agent_name: str | None = None
    agent_status_id: int | None = None
    agent_status_color: str | None = None

    try:
        if session.execute(select(Agent).where(Agent.current_task_id == task.id)).scalar_one_or_none() is None:
            _sync_task_assignment(session, task)
            session.commit()
            session.refresh(task)

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
                .options(selectinload(Agent.role), selectinload(Agent.working_status))
                .where(Agent.current_task_id == task.id)
            )
            .scalars()
            .first()
        )
        if not agent:
            return task, "Нет назначенного агента для задачи."
        agent_name = agent.name
        agent_status_id = agent.working_status_id
        agent_status_color = agent.working_status.color if agent.working_status else None

        api_key = session.execute(
            select(Parameter.value).where(Parameter.key == "API_KEY")
        ).scalar_one_or_none()
        model = session.execute(
            select(Parameter.value).where(Parameter.key == "MODEL")
        ).scalar_one_or_none()
        response, is_completed, error_message = run_task_prompt(
            agent,
            last_message.text,
            api_key,
            model,
            task.id,
            task.status_id,
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
    finally:
        _set_task_running(task_id, False)
        socketio.emit(
            "task_llm_finished",
            {
                "task_id": task_id,
                "agent_name": agent_name,
                "working_status_id": agent_status_id,
                "working_status_color": agent_status_color,
            },
        )
