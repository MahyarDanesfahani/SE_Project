"""create terms and course offerings"""
from alembic import op
import sqlalchemy as sa

revision = "0003_offerings"
down_revision = "0002_curriculum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("terms", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("university_id", sa.Uuid(), nullable=True), sa.Column("title", sa.String(100), nullable=False), sa.Column("academic_year", sa.String(20), nullable=False), sa.Column("semester_number", sa.Integer(), nullable=False), sa.Column("starts_on", sa.Date(), nullable=True), sa.Column("ends_on", sa.Date(), nullable=True), sa.ForeignKeyConstraint(["university_id"], ["universities.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("university_id", "academic_year", "semester_number", name="uq_term_scope"))
    op.create_index("ix_terms_university_id", "terms", ["university_id"], unique=False)
    op.create_table("course_offerings", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("owner_user_id", sa.Uuid(), nullable=False), sa.Column("term_id", sa.Uuid(), nullable=False), sa.Column("course_id", sa.Uuid(), nullable=False), sa.Column("section", sa.String(30), nullable=False), sa.Column("instructor", sa.String(150), nullable=True), sa.Column("capacity", sa.Integer(), nullable=True), sa.Column("credits", sa.Integer(), nullable=False), sa.Column("capacity_updated_at", sa.DateTime(timezone=True), nullable=True), sa.ForeignKeyConstraint(["course_id"], ["courses.id"]), sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]), sa.ForeignKeyConstraint(["term_id"], ["terms.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("owner_user_id", "term_id", "course_id", "section", name="uq_offering_section"))
    op.create_index("ix_course_offerings_owner_user_id", "course_offerings", ["owner_user_id"], unique=False)
    op.create_index("ix_course_offerings_term_id", "course_offerings", ["term_id"], unique=False)
    op.create_index("ix_course_offerings_course_id", "course_offerings", ["course_id"], unique=False)
    op.create_table("class_sessions", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("offering_id", sa.Uuid(), nullable=False), sa.Column("weekday", sa.Integer(), nullable=False), sa.Column("start_time", sa.Time(), nullable=False), sa.Column("end_time", sa.Time(), nullable=False), sa.Column("room", sa.String(100), nullable=True), sa.ForeignKeyConstraint(["offering_id"], ["course_offerings.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_class_sessions_offering_id", "class_sessions", ["offering_id"], unique=False)


def downgrade() -> None:
    op.drop_table("class_sessions")
    op.drop_table("course_offerings")
    op.drop_table("terms")
