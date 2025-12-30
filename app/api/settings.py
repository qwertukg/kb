from __future__ import annotations

from flask import jsonify, request

from ..services import settings as settings_service
from . import api_bp
from .utils import clean_str


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
    values = settings_service.get_settings_values()
    return jsonify(values)


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
    values = {key: clean_str(data.get(key)) for key in settings_service.SETTINGS_KEYS}
    settings_service.update_settings(values)
    return jsonify(values)
