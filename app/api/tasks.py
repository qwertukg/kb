from __future__ import annotations

from flask import jsonify, request

from ..services import tasks as tasks_service
from . import api_bp
from .utils import clean_str, json_error, task_to_dict


@api_bp.get("/tasks")
def api_list_tasks():
    """Список задач.
    ---
    tags:
      - tasks
    responses:
      200:
        description: OK
    """
    tasks = tasks_service.list_tasks()
    return jsonify([task_to_dict(task) for task in tasks])


@api_bp.post("/tasks")
def api_create_task():
    """Создать задачу.
    ---
    tags:
      - tasks
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      201:
        description: Created
    """
    data = request.get_json(silent=True) or {}
    task, error = tasks_service.create_task(
        clean_str(data.get("title")),
        clean_str(data.get("project_id")),
        clean_str(data.get("status_id")),
        clean_str(data.get("author_id")),
        clean_str(data.get("message_text")),
    )
    if error:
        return json_error(error, 400)
    task = tasks_service.get_task_with_messages(task.id)
    return jsonify(task_to_dict(task, include_messages=True)), 201


@api_bp.get("/tasks/<int:task_id>")
def api_get_task(task_id: int):
    """Получить задачу.
    ---
    tags:
      - tasks
    parameters:
      - name: task_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: OK
      404:
        description: Not Found
    """
    task = tasks_service.get_task_with_messages(task_id)
    if not task:
        return json_error("Задача не найдена.", 404)
    return jsonify(task_to_dict(task, include_messages=True))


@api_bp.put("/tasks/<int:task_id>")
def api_update_task(task_id: int):
    """Обновить задачу.
    ---
    tags:
      - tasks
    parameters:
      - name: task_id
        in: path
        required: true
        schema:
          type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: OK
      404:
        description: Not Found
    """
    if not tasks_service.get_task(task_id):
        return json_error("Задача не найдена.", 404)
    data = request.get_json(silent=True) or {}
    task, error = tasks_service.update_task(
        task_id,
        clean_str(data.get("title")),
        clean_str(data.get("project_id")),
        clean_str(data.get("status_id")),
        clean_str(data.get("author_id")),
        clean_str(data.get("message_text")),
    )
    if error:
        return json_error(error, 400)
    task = tasks_service.get_task_with_messages(task_id)
    return jsonify(task_to_dict(task, include_messages=True))


@api_bp.delete("/tasks/<int:task_id>")
def api_delete_task(task_id: int):
    """Удалить задачу.
    ---
    tags:
      - tasks
    parameters:
      - name: task_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      204:
        description: No Content
      404:
        description: Not Found
    """
    error = tasks_service.delete_task(task_id)
    if error:
        return json_error(error, 404)
    return "", 204


@api_bp.patch("/tasks/<int:task_id>/status")
def api_update_task_status(task_id: int):
    """Сменить статус задачи.
    ---
    tags:
      - tasks
    parameters:
      - name: task_id
        in: path
        required: true
        schema:
          type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: OK
      400:
        description: Bad Request
    """
    data = request.get_json(silent=True) or {}
    status_id = data.get("status_id")
    task, error = tasks_service.update_task_status(task_id, clean_str(status_id))
    if error:
        return json_error(error, 400)
    return jsonify({"id": task.id, "status_id": task.status_id})
