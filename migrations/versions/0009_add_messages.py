"""add messages and remove task description

Revision ID: 0009_add_messages
Revises: 0008_seed_agents_tasks
Create Date: 2024-08-19 00:00:08.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0009_add_messages"
down_revision = "0008_seed_agents_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
    )
    with op.batch_alter_table("tasks") as batch:
        batch.drop_column("description")


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch:
        batch.add_column(sa.Column("description", sa.Text(), nullable=False))
    op.drop_table("messages")
