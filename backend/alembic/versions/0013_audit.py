"""create audit logs"""
from alembic import op
import sqlalchemy as sa

revision = "0013_audit"
down_revision = "0012_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("audit_logs", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("actor_user_id", sa.Uuid(), nullable=True), sa.Column("action", sa.String(100), nullable=False), sa.Column("resource_type", sa.String(80), nullable=False), sa.Column("resource_id", sa.String(100), nullable=True), sa.Column("result", sa.String(30), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
