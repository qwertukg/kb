"""create roles

Revision ID: 0001_create_roles
Revises: 
Create Date: 2024-08-19 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_create_roles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("instruction", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("roles")
