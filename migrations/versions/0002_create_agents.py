"""create agents

Revision ID: 0002_create_agents
Revises: 0001_create_roles
Create Date: 2024-08-19 00:00:01.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_create_agents"
down_revision = "0001_create_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("acceptance_criteria", sa.Text(), nullable=True),
        sa.Column("transfer_criteria", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("agents")
