from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from ..services import tasks as tasks_service
from . import bp


@bp.get("/tasks")
def list_tasks() -> str:
    tasks = tasks_service.list_tasks()
    return render_template("tasks/list.html", tasks=tasks)


@bp.get("/tasks/new")
def new_task() -> str:
    boards, statuses, agents, status_agents = tasks_service.get_form_data()
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

    task, error = tasks_service.create_task(board_id, status_id, author_id, message_text)
    if error:
        boards, statuses, agents, status_agents = tasks_service.get_form_data()
        flash(error, "danger")
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

    flash("Задача создана.", "success")
    return redirect(url_for("roles.list_tasks"))


@bp.get("/tasks/<int:task_id>/edit")
def edit_task(task_id: int) -> str:
    task = tasks_service.get_task(task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    boards, statuses, agents, status_agents = tasks_service.get_form_data()
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

    task, error = tasks_service.update_task(
        task_id,
        board_id,
        status_id,
        author_id,
        message_text,
    )
    if error:
        boards, statuses, agents, status_agents = tasks_service.get_form_data()
        task_obj = task or tasks_service.get_task(task_id)
        flash(error, "danger")
        return render_template(
            "tasks/form.html",
            task=task_obj,
            boards=boards,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            board_id=board_id,
            status_id=status_id,
            author_id=author_id,
            message_text=message_text,
        )

    flash("Задача обновлена.", "success")
    return redirect(url_for("roles.list_tasks"))


@bp.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int) -> str:
    error = tasks_service.delete_task(task_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("roles.list_tasks"))

    flash("Задача удалена.", "success")
    return redirect(url_for("roles.list_tasks"))
