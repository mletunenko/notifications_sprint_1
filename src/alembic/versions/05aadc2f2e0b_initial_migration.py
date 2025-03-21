"""Initial migration

Revision ID: 05aadc2f2e0b
Revises:
Create Date: 2025-03-21 12:25:34.189172

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "05aadc2f2e0b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("body", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_templates")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("templates")
