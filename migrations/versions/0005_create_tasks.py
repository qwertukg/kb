"""create tasks

Revision ID: 0005_create_tasks
Revises: 0004_add_agent_kanban_fields
Create Date: 2024-08-19 00:00:04.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_create_tasks"
down_revision = "0004_add_agent_kanban_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status_id", sa.Integer(), sa.ForeignKey("statuses.id"), nullable=False),
        sa.Column("board_id", sa.Integer(), sa.ForeignKey("boards.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("tasks")
