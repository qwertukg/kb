from __future__ import annotations

from flask import flash, jsonify, redirect, render_template, request, url_for
from ..services import tasks as tasks_service
from . import bp


@bp.get("/tasks")
def list_tasks() -> str:
    tasks = tasks_service.list_tasks()
    return render_template("tasks/list.html", tasks=tasks)


@bp.get("/tasks/new")
def new_task() -> str:
    projects, statuses, agents, status_agents = tasks_service.get_form_data()
    return render_template(
        "tasks/form.html",
        task=None,
        projects=projects,
        statuses=statuses,
        status_agents=status_agents,
        agents=agents,
    )


@bp.post("/tasks")
def create_task() -> str:
    title = request.form.get("title", "").strip()
    project_id = request.form.get("project_id", "").strip()
    status_id = request.form.get("status_id", "").strip()
    author_id = request.form.get("author_id", "").strip()
    message_text = request.form.get("message_text", "").strip()

    task, error = tasks_service.create_task(
        title,
        project_id,
        status_id,
        author_id,
        message_text,
    )
    if error:
        projects, statuses, agents, status_agents = tasks_service.get_form_data()
        flash(error, "danger")
        return render_template(
            "tasks/form.html",
            task=None,
            projects=projects,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            title=title,
            project_id=project_id,
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

    projects, statuses, agents, status_agents = tasks_service.get_form_data()
    return render_template(
        "tasks/form.html",
        task=task,
        projects=projects,
        statuses=statuses,
        status_agents=status_agents,
        agents=agents,
    )


@bp.post("/tasks/<int:task_id>")
def update_task(task_id: int) -> str:
    title = request.form.get("title", "").strip()
    project_id = request.form.get("project_id", "").strip()
    status_id = request.form.get("status_id", "").strip()
    author_id = request.form.get("author_id", "").strip()
    message_text = request.form.get("message_text", "").strip()

    task, error = tasks_service.update_task(
        task_id,
        title,
        project_id,
        status_id,
        author_id,
        message_text,
    )
    if error:
        projects, statuses, agents, status_agents = tasks_service.get_form_data()
        task_obj = task or tasks_service.get_task(task_id)
        flash(error, "danger")
        return render_template(
            "tasks/form.html",
            task=task_obj,
            projects=projects,
            statuses=statuses,
            status_agents=status_agents,
            agents=agents,
            title=title,
            project_id=project_id,
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


@bp.get("/tasks/<int:task_id>/messages")
def task_messages(task_id: int):
    task = tasks_service.get_task_with_messages(task_id)
    if not task:
        return jsonify({"error": "Задача не найдена."}), 404

    ordered_messages = sorted(task.messages, key=lambda message: message.id)
    author_ids = {message.author_id for message in ordered_messages}
    assigned_agent = tasks_service.get_task_assigned_agent(task.id)
    messages_html = render_template(
        "tasks/messages.html",
        messages=ordered_messages,
    )
    return jsonify(
        {
            "messages_html": messages_html,
            "message_count": len(ordered_messages),
            "author_count": len(author_ids),
            "agent_name": assigned_agent.name if assigned_agent else None,
            "agent_color": task.status.color if task.status else None,
        }
    )


@bp.post("/tasks/<int:task_id>/status")
def update_task_status(task_id: int):
    data = request.get_json(silent=True) or {}
    status_id = data.get("status_id", "")
    task, error = tasks_service.update_task_status(task_id, str(status_id))
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"ok": True, "task_id": task.id, "status_id": task.status_id})
