"""add user roles"""
from alembic import op
import sqlalchemy as sa

revision = "0014_rbac"
down_revision = "0013_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(30), nullable=False, server_default="student"))
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
