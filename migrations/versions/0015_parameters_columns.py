"""parameters as columns

Revision ID: 0015_parameters_columns
Revises: 0014_add_columns_remove_status_position
Create Date: 2024-10-02 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0015_parameters_columns"
down_revision = "0014_add_columns_remove_status_position"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    columns = [
        row[1]
        for row in connection.execute(sa.text("PRAGMA table_info(parameters)")).fetchall()
    ]
    if "key" not in columns:
        return

    rows = connection.execute(sa.text("SELECT key, value FROM parameters")).fetchall()
    values = {row[0]: row[1] for row in rows}

    op.rename_table("parameters", "parameters_old")
    op.create_table(
        "parameters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("api_key", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("config", sa.Text(), nullable=False),
    )
    if rows:
        connection.execute(
            sa.text(
                "INSERT INTO parameters (id, api_key, model, instructions, config) "
                "VALUES (:id, :api_key, :model, :instructions, :config)"
            ),
            {
                "id": 1,
                "api_key": values.get("API_KEY", ""),
                "model": values.get("MODEL", ""),
                "instructions": values.get("INSTRUCTIONS", ""),
                "config": values.get("CONFIG", ""),
            },
        )
    op.drop_table("parameters_old")


def downgrade() -> None:
    connection = op.get_bind()
    row = connection.execute(
        sa.text("SELECT api_key, model, instructions, config FROM parameters")
    ).fetchone()

    op.rename_table("parameters", "parameters_new")
    op.create_table(
        "parameters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(length=120), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
    )
    if row:
        entries = [
            ("API_KEY", row[0]),
            ("MODEL", row[1]),
            ("INSTRUCTIONS", row[2]),
            ("CONFIG", row[3]),
        ]
        for index, (key, value) in enumerate(entries, start=1):
            connection.execute(
                sa.text(
                    "INSERT INTO parameters (id, key, value) VALUES (:id, :key, :value)"
                ),
                {"id": index, "key": key, "value": value or ""},
            )
    op.drop_table("parameters_new")
