"""create schedule scenario tables"""
from alembic import op
import sqlalchemy as sa

revision = "0004_schedule_scenarios"
down_revision = "0003_offerings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("schedule_scenarios", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("owner_user_id", sa.Uuid(), nullable=False), sa.Column("term_id", sa.Uuid(), nullable=False), sa.Column("name", sa.String(150), nullable=False), sa.Column("score", sa.Integer(), nullable=False), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]), sa.ForeignKeyConstraint(["term_id"], ["terms.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_schedule_scenarios_owner_user_id", "schedule_scenarios", ["owner_user_id"], unique=False)
    op.create_index("ix_schedule_scenarios_term_id", "schedule_scenarios", ["term_id"], unique=False)
    op.create_table("schedule_scenario_items", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("scenario_id", sa.Uuid(), nullable=False), sa.Column("offering_id", sa.Uuid(), nullable=False), sa.ForeignKeyConstraint(["offering_id"], ["course_offerings.id"]), sa.ForeignKeyConstraint(["scenario_id"], ["schedule_scenarios.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_schedule_scenario_items_scenario_id", "schedule_scenario_items", ["scenario_id"], unique=False)
    op.create_index("ix_schedule_scenario_items_offering_id", "schedule_scenario_items", ["offering_id"], unique=False)


def downgrade() -> None:
    op.drop_table("schedule_scenario_items")
    op.drop_table("schedule_scenarios")
