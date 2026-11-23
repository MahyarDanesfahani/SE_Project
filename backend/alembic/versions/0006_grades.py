"""create grade records"""
from alembic import op
import sqlalchemy as sa

revision = "0006_grades"
down_revision = "0005_student_records"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("grade_records", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=False), sa.Column("term_title", sa.String(100), nullable=False), sa.Column("grade", sa.Numeric(4, 2), nullable=True), sa.Column("source", sa.String(30), nullable=False), sa.Column("is_verified", sa.Boolean(), nullable=False), sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("user_id", "course_id", "term_title", name="uq_grade_record"))
    op.create_index("ix_grade_records_user_id", "grade_records", ["user_id"], unique=False)
    op.create_index("ix_grade_records_course_id", "grade_records", ["course_id"], unique=False)


def downgrade() -> None:
    op.drop_table("grade_records")
