"""create teacher feedback tables"""
from alembic import op
import sqlalchemy as sa

revision = "0009_feedback"
down_revision = "0008_announcements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("teacher_surveys", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("owner_user_id", sa.Uuid(), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("teacher_name", sa.String(150), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("minimum_responses", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_teacher_surveys_owner_user_id", "teacher_surveys", ["owner_user_id"], unique=False)
    op.create_index("ix_teacher_surveys_course_id", "teacher_surveys", ["course_id"], unique=False)
    op.create_table("survey_questions", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("survey_id", sa.Uuid(), nullable=False), sa.Column("text", sa.String(300), nullable=False), sa.Column("order_number", sa.Integer(), nullable=False), sa.ForeignKeyConstraint(["survey_id"], ["teacher_surveys.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_survey_questions_survey_id", "survey_questions", ["survey_id"], unique=False)
    op.create_table("survey_responses", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("survey_id", sa.Uuid(), nullable=False), sa.Column("respondent_user_id", sa.Uuid(), nullable=False), sa.Column("answers", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["respondent_user_id"], ["users.id"]), sa.ForeignKeyConstraint(["survey_id"], ["teacher_surveys.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("survey_id", "respondent_user_id", name="uq_survey_response_once"))
    op.create_index("ix_survey_responses_survey_id", "survey_responses", ["survey_id"], unique=False)
    op.create_index("ix_survey_responses_respondent_user_id", "survey_responses", ["respondent_user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("survey_responses")
    op.drop_table("survey_questions")
    op.drop_table("teacher_surveys")
