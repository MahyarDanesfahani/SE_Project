"""create identity tables"""
from alembic import op
import sqlalchemy as sa

revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("universities", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("name", sa.String(150), nullable=False), sa.Column("code", sa.String(50), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_universities_code", "universities", ["code"], unique=True)
    op.create_table("users", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("university_id", sa.Uuid(), nullable=True), sa.ForeignKeyConstraint(["university_id"], ["universities.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_university_id", "users", ["university_id"], unique=False)
    op.create_table("student_profiles", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("full_name", sa.String(150), nullable=True), sa.Column("student_number", sa.String(50), nullable=True), sa.Column("field_of_study", sa.String(150), nullable=True), sa.Column("degree_level", sa.String(50), nullable=True), sa.Column("faculty", sa.String(150), nullable=True), sa.Column("admission_year", sa.Integer(), nullable=True), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("user_id"))
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"], unique=True)
    op.create_index("ix_student_profiles_student_number", "student_profiles", ["student_number"], unique=False)


def downgrade() -> None:
    op.drop_table("student_profiles")
    op.drop_index("ix_users_university_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_universities_code", table_name="universities")
    op.drop_table("universities")
