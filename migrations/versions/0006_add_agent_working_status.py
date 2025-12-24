"""add agent working status

Revision ID: 0006_add_agent_working_status
Revises: 0005_create_tasks
Create Date: 2024-08-19 00:00:05.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_add_agent_working_status"
down_revision = "0005_create_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.add_column(sa.Column("working_status_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_agents_working_status_id", "statuses", ["working_status_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.drop_constraint("fk_agents_working_status_id", type_="foreignkey")
        batch.drop_column("working_status_id")
