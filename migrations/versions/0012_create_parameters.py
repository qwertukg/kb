"""create parameters

Revision ID: 0012_create_parameters
Revises: 0011_add_agent_current_task
Create Date: 2024-10-02 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0012_create_parameters"
down_revision = "0011_add_agent_current_task"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parameters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(length=120), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("parameters")
