from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    agents: Mapped[list["Agent"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    current_task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    success_status_id: Mapped[int | None] = mapped_column(
        ForeignKey("statuses.id"), nullable=True
    )
    error_status_id: Mapped[int | None] = mapped_column(
        ForeignKey("statuses.id"), nullable=True
    )
    working_status_id: Mapped[int | None] = mapped_column(
        ForeignKey("statuses.id"), nullable=True
    )
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    transfer_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[Role] = relationship(back_populates="agents")
    project: Mapped[Project | None] = relationship(foreign_keys=[project_id])
    current_task: Mapped[Task | None] = relationship(foreign_keys=[current_task_id])
    success_status: Mapped[Status | None] = relationship(foreign_keys=[success_status_id])
    error_status: Mapped[Status | None] = relationship(foreign_keys=[error_status_id])
    working_status: Mapped[Status | None] = relationship(
        foreign_keys=[working_status_id], back_populates="working_agents"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    statuses: Mapped[list["Status"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    board: Mapped[list["Column"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Column.position",
    )


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped[Project] = relationship(back_populates="statuses")
    working_agents: Mapped[list[Agent]] = relationship(
        back_populates="working_status", foreign_keys="Agent.working_status_id"
    )
    column: Mapped["Column | None"] = relationship(back_populates="status", uselist=False)


class Column(Base):
    __tablename__ = "columns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position: Mapped[int] = mapped_column(Integer(), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)
    project: Mapped[Project] = relationship(back_populates="board")
    status: Mapped[Status] = relationship(back_populates="column")


class Parameter(Base):
    __tablename__ = "parameters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[Status] = relationship(foreign_keys=[status_id])
    project: Mapped[Project] = relationship(foreign_keys=[project_id])
    messages: Mapped[list["Message"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    task: Mapped[Task] = relationship(back_populates="messages")
    author: Mapped[Agent] = relationship(foreign_keys=[author_id])
