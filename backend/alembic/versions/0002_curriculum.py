"""create curriculum tables"""
from alembic import op
import sqlalchemy as sa

revision = "0002_curriculum"
down_revision = "0001_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("curricula", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("owner_user_id", sa.Uuid(), nullable=False), sa.Column("university_id", sa.Uuid(), nullable=True), sa.Column("title", sa.String(200), nullable=False), sa.Column("major", sa.String(150), nullable=True), sa.Column("admission_year", sa.Integer(), nullable=True), sa.Column("version", sa.String(50), nullable=False), sa.Column("source_name", sa.String(255), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]), sa.ForeignKeyConstraint(["university_id"], ["universities.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_curricula_owner_user_id", "curricula", ["owner_user_id"], unique=False)
    op.create_index("ix_curricula_university_id", "curricula", ["university_id"], unique=False)
    op.create_table("courses", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("code", sa.String(50), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("credits", sa.Integer(), nullable=False), sa.Column("course_type", sa.String(50), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("code", name="uq_courses_code"))
    op.create_index("ix_courses_code", "courses", ["code"], unique=False)
    op.create_table("curriculum_courses", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("curriculum_id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=False), sa.Column("semester_number", sa.Integer(), nullable=True), sa.Column("status", sa.Enum("REQUIRED", "ELECTIVE", "PASSED", "IN_PROGRESS", "REMAINING", name="coursestatus"), nullable=False), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["curriculum_id"], ["curricula.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("curriculum_id", "course_id", name="uq_curriculum_course"))
    op.create_index("ix_curriculum_courses_curriculum_id", "curriculum_courses", ["curriculum_id"], unique=False)
    op.create_index("ix_curriculum_courses_course_id", "curriculum_courses", ["course_id"], unique=False)
    op.create_table("course_prerequisites", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=False), sa.Column("prerequisite_course_id", sa.Uuid(), nullable=False), sa.Column("relation_type", sa.String(20), nullable=False), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["prerequisite_course_id"], ["courses.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("course_id", "prerequisite_course_id", name="uq_course_prerequisite"))
    op.create_index("ix_course_prerequisites_course_id", "course_prerequisites", ["course_id"], unique=False)
    op.create_index("ix_course_prerequisites_prerequisite_course_id", "course_prerequisites", ["prerequisite_course_id"], unique=False)


def downgrade() -> None:
    op.drop_table("course_prerequisites")
    op.drop_table("curriculum_courses")
    op.drop_index("ix_courses_code", table_name="courses")
    op.drop_table("courses")
    op.drop_table("curricula")
    sa.Enum(name="coursestatus").drop(op.get_bind(), checkfirst=True)
