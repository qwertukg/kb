"""add columns and remove status position

Revision ID: 0014_add_columns_remove_status_position
Revises: 0013_rename_board_to_project
Create Date: 2024-10-12 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0014_add_columns_remove_status_position"
down_revision = "0013_rename_board_to_project"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "columns",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("status_id", sa.Integer(), sa.ForeignKey("statuses.id"), nullable=False),
    )
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO columns (position, project_id, status_id)
            SELECT position, project_id, id
            FROM statuses
            """
        )
    )
    with op.batch_alter_table("statuses") as batch:
        batch.drop_column("position")


def downgrade() -> None:
    with op.batch_alter_table("statuses") as batch:
        batch.add_column(sa.Column("position", sa.Integer(), nullable=True))

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE statuses
            SET position = (
                SELECT MIN(columns.position)
                FROM columns
                WHERE columns.status_id = statuses.id
            )
            """
        )
    )
    connection.execute(sa.text("UPDATE statuses SET position = 0 WHERE position IS NULL"))

    with op.batch_alter_table("statuses") as batch:
        batch.alter_column("position", nullable=False)

    op.drop_table("columns")
