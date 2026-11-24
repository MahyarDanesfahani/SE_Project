"""create announcements"""
from alembic import op
import sqlalchemy as sa

revision = "0008_announcements"
down_revision = "0007_planning"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("announcements", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("university_id", sa.Uuid(), nullable=True), sa.Column("title", sa.String(250), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("category", sa.String(80), nullable=False), sa.Column("source_name", sa.String(150), nullable=False), sa.Column("source_url", sa.String(500), nullable=False), sa.Column("published_at", sa.DateTime(timezone=True), nullable=True), sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("is_valid", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["university_id"], ["universities.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("university_id", "source_url", name="uq_announcement_source"))
    op.create_index("ix_announcements_university_id", "announcements", ["university_id"], unique=False)


def downgrade() -> None:
    op.drop_table("announcements")
