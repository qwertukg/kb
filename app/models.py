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
    board_id: Mapped[int | None] = mapped_column(ForeignKey("boards.id"), nullable=True)
    success_status_id: Mapped[int | None] = mapped_column(
        ForeignKey("statuses.id"), nullable=True
    )
    error_status_id: Mapped[int | None] = mapped_column(
        ForeignKey("statuses.id"), nullable=True
    )
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    transfer_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[Role] = relationship(back_populates="agents")
    board: Mapped[Board | None] = relationship(foreign_keys=[board_id])
    success_status: Mapped[Status | None] = relationship(foreign_keys=[success_status_id])
    error_status: Mapped[Status | None] = relationship(foreign_keys=[error_status_id])


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    statuses: Mapped[list["Status"]] = relationship(
        back_populates="board", cascade="all, delete-orphan"
    )


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    position: Mapped[int] = mapped_column(Integer(), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    board: Mapped[Board] = relationship(back_populates="statuses")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    status: Mapped[Status] = relationship(foreign_keys=[status_id])
    board: Mapped[Board] = relationship(foreign_keys=[board_id])
