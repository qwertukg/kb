"""add agent kanban fields

Revision ID: 0004_add_agent_kanban_fields
Revises: 0003_create_boards_statuses
Create Date: 2024-08-19 00:00:03.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_add_agent_kanban_fields"
down_revision = "0003_create_boards_statuses"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.add_column(sa.Column("board_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("success_status_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("error_status_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_agents_board_id", "boards", ["board_id"], ["id"])
        batch.create_foreign_key(
            "fk_agents_success_status_id", "statuses", ["success_status_id"], ["id"]
        )
        batch.create_foreign_key(
            "fk_agents_error_status_id", "statuses", ["error_status_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.drop_constraint("fk_agents_error_status_id", type_="foreignkey")
        batch.drop_constraint("fk_agents_success_status_id", type_="foreignkey")
        batch.drop_constraint("fk_agents_board_id", type_="foreignkey")
        batch.drop_column("error_status_id")
        batch.drop_column("success_status_id")
        batch.drop_column("board_id")
