"""create student course records"""
from alembic import op
import sqlalchemy as sa

revision = "0005_student_records"
down_revision = "0004_schedule_scenarios"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("student_course_records", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=False), sa.Column("term_title", sa.String(100), nullable=True), sa.Column("status", sa.String(30), nullable=False), sa.Column("grade", sa.Integer(), nullable=True), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("user_id", "course_id", "term_title", name="uq_student_course_record"))
    op.create_index("ix_student_course_records_user_id", "student_course_records", ["user_id"], unique=False)
    op.create_index("ix_student_course_records_course_id", "student_course_records", ["course_id"], unique=False)


def downgrade() -> None:
    op.drop_table("student_course_records")
