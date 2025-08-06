from alembic import op
import sqlalchemy as sa

revision = "006_add_conversation_vector"
down_revision = "005_add_exhibit_order"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("conversation", sa.Column("vector_id", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("conversation", "vector_id")
