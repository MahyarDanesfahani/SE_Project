"""create AI conversation tables"""
from alembic import op
import sqlalchemy as sa

revision = "0011_ai"
down_revision = "0010_meal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("ai_conversations", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_conversations_user_id", "ai_conversations", ["user_id"], unique=False)
    op.create_table("ai_messages", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("conversation_id", sa.Uuid(), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("provider", sa.String(50), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_messages_conversation_id", "ai_messages", ["conversation_id"], unique=False)


def downgrade() -> None:
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
