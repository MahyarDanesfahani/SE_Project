"""create meal demo tables"""
from alembic import op
import sqlalchemy as sa

revision = "0010_meal"
down_revision = "0009_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("meal_menu_items", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("university_id", sa.Uuid(), nullable=True), sa.Column("service_date", sa.Date(), nullable=False), sa.Column("meal_type", sa.String(30), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("price", sa.Integer(), nullable=True), sa.Column("source_name", sa.String(150), nullable=False), sa.Column("source_url", sa.String(500), nullable=False), sa.ForeignKeyConstraint(["university_id"], ["universities.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("university_id", "service_date", "meal_type", name="uq_meal_menu_slot"))
    op.create_index("ix_meal_menu_items_university_id", "meal_menu_items", ["university_id"], unique=False)
    op.create_table("meal_reservations", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("menu_item_id", sa.Uuid(), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("external_reference", sa.String(100), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.ForeignKeyConstraint(["menu_item_id"], ["meal_menu_items.id"]), sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_meal_reservations_user_id", "meal_reservations", ["user_id"], unique=False)
    op.create_index("ix_meal_reservations_menu_item_id", "meal_reservations", ["menu_item_id"], unique=False)


def downgrade() -> None:
    op.drop_table("meal_reservations")
    op.drop_table("meal_menu_items")
