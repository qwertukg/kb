from __future__ import annotations

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from .schemas import (
    AgentSchema,
    MessageSchema,
    ProjectSchema,
    RoleSchema,
    SettingsSchema,
    StatusSchema,
    TaskSchema,
)


def build_swagger_template() -> dict[str, object]:
    spec = APISpec(
        title="KB Admin API",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[MarshmallowPlugin()],
    )

    spec.components.schema("Role", schema=RoleSchema)
    spec.components.schema("Agent", schema=AgentSchema)
    spec.components.schema("Project", schema=ProjectSchema)
    spec.components.schema("Status", schema=StatusSchema)
    spec.components.schema("Task", schema=TaskSchema)
    spec.components.schema("Message", schema=MessageSchema)
    spec.components.schema("Settings", schema=SettingsSchema)

    template = spec.to_dict()
    return template
