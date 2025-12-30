from __future__ import annotations

from sqlalchemy import select

from ..db import SessionLocal
from ..models import Settings


def get_settings() -> Settings:
    session = SessionLocal()
    settings = session.execute(select(Settings)).scalars().first()
    if not settings:
        settings = Settings(api_key="", model="", instructions="", config="")
        session.add(settings)
        session.commit()
    return settings


def update_settings(
    api_key: str,
    model: str,
    instructions: str,
    config: str,
) -> Settings:
    session = SessionLocal()
    settings = session.execute(select(Settings)).scalars().first()
    if not settings:
        settings = Settings(api_key="", model="", instructions="", config="")
        session.add(settings)
        session.flush()

    settings.api_key = api_key
    settings.model = model
    settings.instructions = instructions
    settings.config = config
    session.commit()
    return settings
