from __future__ import annotations

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..models import Agent, Message, Project, Role, Settings, Status, Task


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True


class AgentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Agent
        load_instance = True


class ProjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True


class StatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Status
        load_instance = True


class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True


class MessageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        load_instance = True


class SettingsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Settings
        load_instance = True
