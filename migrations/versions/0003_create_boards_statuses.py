"""create boards and statuses

Revision ID: 0003_create_boards_statuses
Revises: 0002_create_agents
Create Date: 2024-08-19 00:00:02.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_create_boards_statuses"
down_revision = "0002_create_agents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "boards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
    )
    op.create_table(
        "statuses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("board_id", sa.Integer(), sa.ForeignKey("boards.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("statuses")
    op.drop_table("boards")
