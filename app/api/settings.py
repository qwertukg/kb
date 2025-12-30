from __future__ import annotations

from flask import jsonify, request

from ..services import settings as settings_service
from . import api_bp
from .utils import clean_str, settings_to_dict


@api_bp.get("/settings")
def api_get_settings():
    """Получить настройки.
    ---
    tags:
      - settings
    responses:
      200:
        description: OK
    """
    settings = settings_service.get_settings()
    return jsonify(settings_to_dict(settings))


@api_bp.put("/settings")
def api_update_settings():
    """Обновить настройки.
    ---
    tags:
      - settings
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: OK
    """
    data = request.get_json(silent=True) or {}
    settings = settings_service.update_settings(
        clean_str(data.get("api_key")),
        clean_str(data.get("model")),
        clean_str(data.get("instructions")),
        clean_str(data.get("config")),
    )
    return jsonify(settings_to_dict(settings))
