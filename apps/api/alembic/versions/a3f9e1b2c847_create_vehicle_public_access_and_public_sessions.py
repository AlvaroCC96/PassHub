"""create vehicle_public_access and public_sessions

Revision ID: a3f9e1b2c847
Revises: 587495e3332d
Create Date: 2026-07-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a3f9e1b2c847"
down_revision: str | None = "587495e3332d"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vehicle_public_access",
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("public_token", sa.String(length=64), nullable=False),
        sa.Column("pin_hash", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_access_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vehicle_id", name="uq_vehicle_public_access_vehicle_id"),
        sa.UniqueConstraint("public_token", name="uq_vehicle_public_access_public_token"),
    )
    op.create_index(
        "ix_vehicle_public_access_vehicle_id", "vehicle_public_access", ["vehicle_id"], unique=False
    )
    op.create_index(
        "ix_vehicle_public_access_public_token",
        "vehicle_public_access",
        ["public_token"],
        unique=False,
    )

    op.create_table(
        "public_sessions",
        sa.Column("vehicle_public_access_id", sa.UUID(), nullable=False),
        sa.Column("session_token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_public_sessions_vehicle_public_access_id",
        "public_sessions",
        ["vehicle_public_access_id"],
        unique=False,
    )
    op.create_index(
        "ix_public_sessions_expires_at", "public_sessions", ["expires_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_public_sessions_expires_at", table_name="public_sessions")
    op.drop_index(
        "ix_public_sessions_vehicle_public_access_id", table_name="public_sessions"
    )
    op.drop_table("public_sessions")
    op.drop_index(
        "ix_vehicle_public_access_public_token", table_name="vehicle_public_access"
    )
    op.drop_index(
        "ix_vehicle_public_access_vehicle_id", table_name="vehicle_public_access"
    )
    op.drop_table("vehicle_public_access")
