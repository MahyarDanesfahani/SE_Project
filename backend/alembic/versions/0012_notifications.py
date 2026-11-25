"""create in-app notifications"""
from alembic import op
import sqlalchemy as sa

revision = "0012_notifications"
down_revision = "0011_ai"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("notifications", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("channel", sa.String(30), nullable=False), sa.Column("is_read", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("notifications")
