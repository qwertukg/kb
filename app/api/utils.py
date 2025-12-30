from __future__ import annotations

from collections.abc import Iterable

from flask import jsonify


def json_error(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


def clean_str(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def optional_str(value: object) -> str | None:
    cleaned = clean_str(value)
    return cleaned or None


def normalize_board_rows(board_rows: object) -> list[dict[str, str]] | None:
    if board_rows is None:
        return []
    if not isinstance(board_rows, Iterable) or isinstance(board_rows, (str, bytes)):
        return None

    normalized: list[dict[str, str]] = []
    for row in board_rows:
        if not isinstance(row, dict):
            return None
        is_deleted = row.get("is_deleted")
        normalized.append(
            {
                "column_id": clean_str(row.get("column_id")),
                "status_id": clean_str(row.get("status_id")),
                "position": clean_str(row.get("position")),
                "is_deleted": "1" if str(is_deleted).lower() in {"1", "true", "yes"} else "",
            }
        )
    return normalized


def role_to_dict(role) -> dict[str, object]:
    return {
        "id": role.id,
        "name": role.name,
        "instruction": role.instruction,
    }


def agent_to_dict(agent) -> dict[str, object]:
    return {
        "id": agent.id,
        "name": agent.name,
        "role_id": agent.role_id,
        "project_id": agent.project_id,
        "current_task_id": agent.current_task_id,
        "success_status_id": agent.success_status_id,
        "error_status_id": agent.error_status_id,
        "working_status_id": agent.working_status_id,
        "acceptance_criteria": agent.acceptance_criteria,
        "transfer_criteria": agent.transfer_criteria,
    }


def project_to_dict(project, include_board: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {"id": project.id, "name": project.name}
    if include_board:
        payload["board"] = [
            {"id": column.id, "position": column.position, "status_id": column.status_id}
            for column in sorted(project.board, key=lambda column: column.position)
        ]
    return payload


def status_to_dict(status) -> dict[str, object]:
    return {
        "id": status.id,
        "name": status.name,
        "color": status.color,
        "project_id": status.project_id,
    }


def task_to_dict(task, include_messages: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": task.id,
        "title": task.title,
        "project_id": task.project_id,
        "status_id": task.status_id,
    }
    if include_messages:
        payload["messages"] = [
            {"id": message.id, "author_id": message.author_id, "text": message.text}
            for message in sorted(task.messages, key=lambda message: message.id)
        ]
    else:
        payload["message_count"] = len(task.messages or [])
    return payload


def settings_to_dict(settings) -> dict[str, object]:
    return {
        "id": settings.id,
        "api_key": settings.api_key,
        "model": settings.model,
        "instructions": settings.instructions,
        "config": settings.config,
    }
