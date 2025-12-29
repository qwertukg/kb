"""rename boards to projects

Revision ID: 0013_rename_board_to_project
Revises: 0012_create_parameters
Create Date: 2024-10-02 00:00:01.000000

"""
from __future__ import annotations

from alembic import op


revision = "0013_rename_board_to_project"
down_revision = "0012_create_parameters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("boards", "projects")
    with op.batch_alter_table("statuses") as batch:
        batch.alter_column("board_id", new_column_name="project_id")
    with op.batch_alter_table("tasks") as batch:
        batch.alter_column("board_id", new_column_name="project_id")
    with op.batch_alter_table("agents") as batch:
        batch.alter_column("board_id", new_column_name="project_id")


def downgrade() -> None:
    with op.batch_alter_table("agents") as batch:
        batch.alter_column("project_id", new_column_name="board_id")
    with op.batch_alter_table("tasks") as batch:
        batch.alter_column("project_id", new_column_name="board_id")
    with op.batch_alter_table("statuses") as batch:
        batch.alter_column("project_id", new_column_name="board_id")
    op.rename_table("projects", "boards")
