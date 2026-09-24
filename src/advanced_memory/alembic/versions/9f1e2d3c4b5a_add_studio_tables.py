"""add studio tables

Revision ID: 9f1e2d3c4b5a
Revises: 6a8b2c3d4e5f
Create Date: 2026-09-24 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f1e2d3c4b5a"
down_revision: str | None = "6a8b2c3d4e5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add SkillStudio tables (isolated studio_* namespace)."""
    op.create_table(
        "studio_scenarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("should_fire", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_studio_scenarios_skill", "studio_scenarios", ["skill_id"])

    op.create_table(
        "studio_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False, server_default=""),
        sa.Column("precision", sa.Float(), nullable=False, server_default="0"),
        sa.Column("recall", sa.Float(), nullable=False, server_default="0"),
        sa.Column("verdicts_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_studio_runs_skill", "studio_runs", ["skill_id"])

    op.create_table(
        "studio_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("section", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_studio_events_skill", "studio_events", ["skill_id"])

    op.create_table(
        "studio_distill_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("draft_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("state", sa.String(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_studio_distill_skill", "studio_distill_jobs", ["skill_id"])


def downgrade() -> None:
    """Remove SkillStudio tables."""
    op.drop_index("idx_studio_distill_skill", table_name="studio_distill_jobs")
    op.drop_table("studio_distill_jobs")
    op.drop_index("idx_studio_events_skill", table_name="studio_events")
    op.drop_table("studio_events")
    op.drop_index("idx_studio_runs_skill", table_name="studio_runs")
    op.drop_table("studio_runs")
    op.drop_index("idx_studio_scenarios_skill", table_name="studio_scenarios")
    op.drop_table("studio_scenarios")
