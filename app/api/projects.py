from __future__ import annotations

from flask import jsonify, request

from ..services import projects as projects_service
from . import api_bp
from .utils import clean_str, json_error, normalize_board_rows, project_to_dict


@api_bp.get("/projects")
def api_list_projects():
    """Список проектов.
    ---
    tags:
      - projects
    responses:
      200:
        description: OK
    """
    projects = projects_service.list_projects()
    return jsonify([project_to_dict(project) for project in projects])


@api_bp.post("/projects")
def api_create_project():
    """Создать проект.
    ---
    tags:
      - projects
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
    board_rows = normalize_board_rows(data.get("board_rows"))
    if board_rows is None:
        return json_error("Неверный формат доски.", 400)
    project, error = projects_service.create_project(clean_str(data.get("name")), board_rows)
    if error:
        return json_error(error, 400)
    return jsonify(project_to_dict(project, include_board=True)), 201


@api_bp.get("/projects/<int:project_id>")
def api_get_project(project_id: int):
    """Получить проект.
    ---
    tags:
      - projects
    parameters:
      - name: project_id
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
    project = projects_service.get_project_with_board(project_id)
    if not project:
        return json_error("Проект не найден.", 404)
    return jsonify(project_to_dict(project, include_board=True))


@api_bp.put("/projects/<int:project_id>")
def api_update_project(project_id: int):
    """Обновить проект.
    ---
    tags:
      - projects
    parameters:
      - name: project_id
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
    if not projects_service.get_project(project_id):
        return json_error("Проект не найден.", 404)
    data = request.get_json(silent=True) or {}
    board_rows = normalize_board_rows(data.get("board_rows"))
    if board_rows is None:
        return json_error("Неверный формат доски.", 400)
    project, error = projects_service.update_project(
        project_id,
        clean_str(data.get("name")),
        board_rows,
    )
    if error:
        return json_error(error, 400)
    project = projects_service.get_project_with_board(project_id)
    return jsonify(project_to_dict(project, include_board=True))


@api_bp.delete("/projects/<int:project_id>")
def api_delete_project(project_id: int):
    """Удалить проект.
    ---
    tags:
      - projects
    parameters:
      - name: project_id
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
    error = projects_service.delete_project(project_id)
    if error:
        return json_error(error, 404)
    return "", 204
