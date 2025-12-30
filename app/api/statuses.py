from __future__ import annotations

from flask import jsonify, request

from ..services import statuses as statuses_service
from . import api_bp
from .utils import clean_str, json_error, status_to_dict


@api_bp.get("/statuses")
def api_list_statuses():
    """Список статусов.
    ---
    tags:
      - statuses
    responses:
      200:
        description: OK
    """
    statuses = statuses_service.list_statuses()
    return jsonify([status_to_dict(status) for status in statuses])


@api_bp.post("/statuses")
def api_create_status():
    """Создать статус.
    ---
    tags:
      - statuses
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
    status, error = statuses_service.create_status(
        clean_str(data.get("name")),
        clean_str(data.get("color")),
        clean_str(data.get("project_id")),
    )
    if error:
        return json_error(error, 400)
    return jsonify(status_to_dict(status)), 201


@api_bp.get("/statuses/<int:status_id>")
def api_get_status(status_id: int):
    """Получить статус.
    ---
    tags:
      - statuses
    parameters:
      - name: status_id
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
    status = statuses_service.get_status(status_id)
    if not status:
        return json_error("Статус не найден.", 404)
    return jsonify(status_to_dict(status))


@api_bp.put("/statuses/<int:status_id>")
def api_update_status(status_id: int):
    """Обновить статус.
    ---
    tags:
      - statuses
    parameters:
      - name: status_id
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
    if not statuses_service.get_status(status_id):
        return json_error("Статус не найден.", 404)
    data = request.get_json(silent=True) or {}
    status, error = statuses_service.update_status(
        status_id,
        clean_str(data.get("name")),
        clean_str(data.get("color")),
        clean_str(data.get("project_id")),
    )
    if error:
        return json_error(error, 400)
    return jsonify(status_to_dict(status))


@api_bp.delete("/statuses/<int:status_id>")
def api_delete_status(status_id: int):
    """Удалить статус.
    ---
    tags:
      - statuses
    parameters:
      - name: status_id
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
    error = statuses_service.delete_status(status_id)
    if error:
        return json_error(error, 404)
    return "", 204
