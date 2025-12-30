from __future__ import annotations

from flask import jsonify, request

from ..services import settings as settings_service
from . import api_bp
from .utils import clean_str, json_error, parameter_to_dict


@api_bp.get("/parameters")
def api_list_parameters():
    """Список параметров.
    ---
    tags:
      - parameters
    responses:
      200:
        description: OK
    """
    parameters = settings_service.list_parameters()
    return jsonify([parameter_to_dict(parameter) for parameter in parameters])


@api_bp.post("/parameters")
def api_create_parameter():
    """Создать/обновить параметр.
    ---
    tags:
      - parameters
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
    parameter, error = settings_service.create_parameter(
        clean_str(data.get("key")),
        clean_str(data.get("value")),
    )
    if error:
        return json_error(error, 400)
    return jsonify(parameter_to_dict(parameter)), 201


@api_bp.get("/parameters/<int:parameter_id>")
def api_get_parameter(parameter_id: int):
    """Получить параметры.
    ---
    tags:
      - parameters
    parameters:
      - name: parameter_id
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
    parameter = settings_service.get_parameter(parameter_id)
    if not parameter:
        return json_error("Параметр не найден.", 404)
    return jsonify(parameter_to_dict(parameter))


@api_bp.put("/parameters/<int:parameter_id>")
def api_update_parameter(parameter_id: int):
    """Обновить параметры.
    ---
    tags:
      - parameters
    parameters:
      - name: parameter_id
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
    if not settings_service.get_parameter(parameter_id):
        return json_error("Параметр не найден.", 404)
    data = request.get_json(silent=True) or {}
    parameter, error = settings_service.update_parameter(
        parameter_id,
        clean_str(data.get("key")),
        clean_str(data.get("value")),
    )
    if error:
        return json_error(error, 400)
    return jsonify(parameter_to_dict(parameter))


@api_bp.delete("/parameters/<int:parameter_id>")
def api_delete_parameter(parameter_id: int):
    """Удалить параметры.
    ---
    tags:
      - parameters
    parameters:
      - name: parameter_id
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
    error = settings_service.delete_parameter(parameter_id)
    if error:
        return json_error(error, 404)
    return "", 204
