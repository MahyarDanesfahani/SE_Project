"""create exams and tasks"""
from alembic import op
import sqlalchemy as sa

revision = "0007_planning"
down_revision = "0006_grades"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("exams", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("owner_user_id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=False), sa.Column("term_title", sa.String(100), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("location", sa.String(150), nullable=True), sa.Column("notes", sa.Text(), nullable=True), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_exams_owner_user_id", "exams", ["owner_user_id"], unique=False)
    op.create_index("ix_exams_course_id", "exams", ["course_id"], unique=False)
    op.create_table("tasks", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("owner_user_id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=True), sa.Column("title", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=True), sa.Column("due_at", sa.DateTime(timezone=True), nullable=True), sa.Column("priority", sa.Integer(), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("owner_user_id", "title", "due_at", name="uq_task_identity"))
    op.create_index("ix_tasks_owner_user_id", "tasks", ["owner_user_id"], unique=False)
    op.create_index("ix_tasks_course_id", "tasks", ["course_id"], unique=False)


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("exams")
