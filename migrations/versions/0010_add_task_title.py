"""add task title

Revision ID: 0010_add_task_title
Revises: 0009_add_messages
Create Date: 2024-10-02 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0010_add_task_title"
down_revision = "0009_add_messages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("tasks") as batch:
        batch.add_column(sa.Column("title", sa.String(200), nullable=False, server_default=""))


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch:
        batch.drop_column("title")
