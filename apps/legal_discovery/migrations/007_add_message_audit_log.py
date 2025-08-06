"""Add message audit log"""

from alembic import op
import sqlalchemy as sa

revision = "007_add_message_audit_log"
down_revision = "006_add_conversation_vector"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "message_audit_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("message_id", sa.String(length=36), sa.ForeignKey("message.id"), nullable=False),
        sa.Column("sender", sa.String(length=50), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("voice_model", sa.String(length=50), nullable=True),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("message_audit_log")
