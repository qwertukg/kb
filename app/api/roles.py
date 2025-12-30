from __future__ import annotations

from flask import jsonify, request

from ..services import roles as roles_service
from . import api_bp
from .utils import clean_str, json_error, optional_str, role_to_dict


@api_bp.get("/roles")
def api_list_roles():
    """Список ролей.
    ---
    tags:
      - roles
    responses:
      200:
        description: OK
    """
    roles = roles_service.list_roles()
    return jsonify([role_to_dict(role) for role in roles])


@api_bp.post("/roles")
def api_create_role():
    """Создать роль.
    ---
    tags:
      - roles
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
    name = clean_str(data.get("name"))
    instruction = optional_str(data.get("instruction"))
    role, error = roles_service.create_role(name, instruction)
    if error:
        return json_error(error, 400)
    return jsonify(role_to_dict(role)), 201


@api_bp.get("/roles/<int:role_id>")
def api_get_role(role_id: int):
    """Получить роль.
    ---
    tags:
      - roles
    parameters:
      - name: role_id
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
    role = roles_service.get_role(role_id)
    if not role:
        return json_error("Роль не найдена.", 404)
    return jsonify(role_to_dict(role))


@api_bp.put("/roles/<int:role_id>")
def api_update_role(role_id: int):
    """Обновить роль.
    ---
    tags:
      - roles
    parameters:
      - name: role_id
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
    if not roles_service.get_role(role_id):
        return json_error("Роль не найдена.", 404)
    data = request.get_json(silent=True) or {}
    name = clean_str(data.get("name"))
    instruction = optional_str(data.get("instruction"))
    role, error = roles_service.update_role(role_id, name, instruction)
    if error:
        return json_error(error, 400)
    return jsonify(role_to_dict(role))


@api_bp.delete("/roles/<int:role_id>")
def api_delete_role(role_id: int):
    """Удалить роль.
    ---
    tags:
      - roles
    parameters:
      - name: role_id
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
    error = roles_service.delete_role(role_id)
    if error:
        return json_error(error, 404)
    return "", 204
