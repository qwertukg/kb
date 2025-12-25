from __future__ import annotations

from collections import defaultdict

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db import SessionLocal
from ..models import Agent, Board, Message, Status, Task
from . import bp


def build_status_agents(session: SessionLocal) -> dict[int, list[str]]:
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents: dict[int, list[str]] = defaultdict(list)
    for agent in agents:
        if agent.working_status_id:
            status_agents[agent.working_status_id].append(agent.name)
    return status_agents


@bp.get("/tasks")
def list_tasks() -> str:
    session = SessionLocal()
    tasks = (
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
    return render_template("tasks/list.html", tasks=tasks)


@bp.get("/tasks/new")
def new_task() -> str:
    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents = build_status_agents(session)
    return render_template(
        "tasks/form.html",
        task=None,
        boards=boards,
        statuses=statuses,
        status_agents=status_agents,
        agents=agents,
    )


@bp.post("/tasks")
def create_task() -> str:
    board_id = request.form.get("board_id", "").strip()
    status_id = request.form.get("status_id", "").strip()
    author_id = request.form.get("author_id", "").strip()
    message_text = request.form.get("message_text", "").strip()

    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents = build_status_agents(session)

    if not board_id or not status_id or not author_id or not message_text:
        flash("Доска, статус, автор и сообщение обязательны.", "danger")
        return render_template(
            "tasks/form.html",
            task=None,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            board_id=board_id,
            status_id=status_id,
            author_id=author_id,
            message_text=message_text,
        )

    board = session.get(Board, int(board_id))
    status = session.get(Status, int(status_id))
    author = session.get(Agent, int(author_id)) if author_id else None
    if not board or not status or status.board_id != board.id or not author:
        flash("Проверьте доску, статус и автора.", "danger")
        return render_template(
            "tasks/form.html",
            task=None,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            board_id=board_id,
            status_id=status_id,
            author_id=author_id,
            message_text=message_text,
        )

    task = Task(board_id=board.id, status_id=status.id)
    session.add(task)
    session.flush()
    session.add(Message(task_id=task.id, author_id=author.id, text=message_text))
    session.commit()
    flash("Задача создана.", "success")
    return redirect(url_for("roles.list_tasks"))


@bp.get("/tasks/<int:task_id>/edit")
def edit_task(task_id: int) -> str:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents = build_status_agents(session)
    return render_template(
        "tasks/form.html",
        task=task,
        boards=boards,
        statuses=statuses,
        status_agents=status_agents,
        agents=agents,
    )


@bp.post("/tasks/<int:task_id>")
def update_task(task_id: int) -> str:
    board_id = request.form.get("board_id", "").strip()
    status_id = request.form.get("status_id", "").strip()
    author_id = request.form.get("author_id", "").strip()
    message_text = request.form.get("message_text", "").strip()

    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    agents = session.execute(select(Agent).order_by(Agent.name)).scalars().all()
    status_agents = build_status_agents(session)

    if not board_id or not status_id:
        flash("Доска и статус обязательны.", "danger")
        return render_template(
            "tasks/form.html",
            task=task,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            board_id=board_id,
            status_id=status_id,
            author_id=author_id,
            message_text=message_text,
        )

    board = session.get(Board, int(board_id))
    status = session.get(Status, int(status_id))
    author = session.get(Agent, int(author_id)) if author_id else None
    if not board or not status or status.board_id != board.id:
        flash("Статус должен принадлежать выбранной доске.", "danger")
        return render_template(
            "tasks/form.html",
            task=task,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            board_id=board_id,
            status_id=status_id,
            author_id=author_id,
            message_text=message_text,
        )
    if message_text and not author:
        flash("Выберите автора для сообщения.", "danger")
        return render_template(
            "tasks/form.html",
            task=task,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            board_id=board_id,
            status_id=status_id,
            author_id=author_id,
            message_text=message_text,
        )

    task.board_id = board.id
    task.status_id = status.id
    if message_text:
        session.add(Message(task_id=task.id, author_id=author.id, text=message_text))
    session.commit()
    flash("Задача обновлена.", "success")
    return redirect(url_for("roles.list_tasks"))


@bp.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int) -> str:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    session.delete(task)
    session.commit()
    flash("Задача удалена.", "success")
    return redirect(url_for("roles.list_tasks"))
