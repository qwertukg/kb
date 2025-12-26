"""add agent current task

Revision ID: 0011_add_agent_current_task
Revises: 0010_add_task_title
Create Date: 2024-10-02 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0011_add_agent_current_task"
down_revision = "0010_add_task_title"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.add_column(sa.Column("current_task_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_agents_current_task_id_tasks",
            "tasks",
            ["current_task_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.drop_constraint("fk_agents_current_task_id_tasks", type_="foreignkey")
        batch.drop_column("current_task_id")
