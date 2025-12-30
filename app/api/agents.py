from __future__ import annotations

from flask import jsonify, request

from ..services import agents as agents_service
from . import api_bp
from .utils import agent_to_dict, clean_str, json_error, optional_str


@api_bp.get("/agents")
def api_list_agents():
    """Список агентов.
    ---
    tags:
      - agents
    responses:
      200:
        description: OK
    """
    agents = agents_service.list_agents()
    return jsonify([agent_to_dict(agent) for agent in agents])


@api_bp.post("/agents")
def api_create_agent():
    """Создать агента.
    ---
    tags:
      - agents
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
    agent, error = agents_service.create_agent(
        clean_str(data.get("name")),
        clean_str(data.get("role_id")),
        clean_str(data.get("project_id")),
        clean_str(data.get("success_status_id")),
        clean_str(data.get("error_status_id")),
        clean_str(data.get("working_status_id")),
        optional_str(data.get("acceptance_criteria")),
        optional_str(data.get("transfer_criteria")),
    )
    if error:
        return json_error(error, 400)
    return jsonify(agent_to_dict(agent)), 201


@api_bp.get("/agents/<int:agent_id>")
def api_get_agent(agent_id: int):
    """Получить агента.
    ---
    tags:
      - agents
    parameters:
      - name: agent_id
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
    agent = agents_service.get_agent(agent_id)
    if not agent:
        return json_error("Агент не найден.", 404)
    return jsonify(agent_to_dict(agent))


@api_bp.put("/agents/<int:agent_id>")
def api_update_agent(agent_id: int):
    """Обновить агента.
    ---
    tags:
      - agents
    parameters:
      - name: agent_id
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
    if not agents_service.get_agent(agent_id):
        return json_error("Агент не найден.", 404)
    data = request.get_json(silent=True) or {}
    agent, error = agents_service.update_agent(
        agent_id,
        clean_str(data.get("name")),
        clean_str(data.get("role_id")),
        clean_str(data.get("project_id")),
        clean_str(data.get("success_status_id")),
        clean_str(data.get("error_status_id")),
        clean_str(data.get("working_status_id")),
        optional_str(data.get("acceptance_criteria")),
        optional_str(data.get("transfer_criteria")),
    )
    if error:
        return json_error(error, 400)
    return jsonify(agent_to_dict(agent))


@api_bp.delete("/agents/<int:agent_id>")
def api_delete_agent(agent_id: int):
    """Удалить агента.
    ---
    tags:
      - agents
    parameters:
      - name: agent_id
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
    error = agents_service.delete_agent(agent_id)
    if error:
        return json_error(error, 404)
    return "", 204
