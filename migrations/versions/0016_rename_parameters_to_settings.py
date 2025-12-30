"""rename parameters to settings

Revision ID: 0016_rename_parameters_to_settings
Revises: 0015_parameters_columns
Create Date: 2024-10-02 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0016_rename_parameters_to_settings"
down_revision = "0015_parameters_columns"
branch_labels = None
depends_on = None


def _table_names(connection) -> set[str]:
    rows = connection.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table'")
    ).fetchall()
    return {row[0] for row in rows}


def upgrade() -> None:
    connection = op.get_bind()
    tables = _table_names(connection)
    if "settings" in tables:
        return
    if "parameters" in tables:
        op.rename_table("parameters", "settings")
        return

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("api_key", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("config", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    connection = op.get_bind()
    tables = _table_names(connection)
    if "parameters" in tables:
        return
    if "settings" in tables:
        op.rename_table("settings", "parameters")
