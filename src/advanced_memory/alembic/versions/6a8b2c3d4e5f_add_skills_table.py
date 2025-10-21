"""add skills table

Revision ID: 6a8b2c3d4e5f
Revises: 5fe1ab1ccebe
Create Date: 2025-10-21 15:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6a8b2c3d4e5f"
down_revision: str | None = "5fe1ab1ccebe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add skills table for Claude Skills integration."""
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.Integer(), sa.ForeignKey("entities.id"), nullable=True),
        sa.Column("version", sa.String(), nullable=False, server_default="1.0.0"),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("difficulty", sa.String(), nullable=True),
        sa.Column("license", sa.String(), nullable=True),
        sa.Column("allowed_tools", sa.Text(), nullable=True),  # JSON array
        sa.Column("custom_metadata", sa.Text(), nullable=True),  # JSON object
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("effectiveness_rating", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Create indexes for common queries
    op.create_index("idx_skills_name", "skills", ["name"])
    op.create_index("idx_skills_category", "skills", ["category"])
    op.create_index("idx_skills_entity_id", "skills", ["entity_id"])


def downgrade() -> None:
    """Remove skills table."""
    op.drop_index("idx_skills_entity_id", table_name="skills")
    op.drop_index("idx_skills_category", table_name="skills")
    op.drop_index("idx_skills_name", table_name="skills")
    op.drop_table("skills")
