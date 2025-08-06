"""Create conversation and message tables"""

from alembic import op
import sqlalchemy as sa

revision = "002_add_chat_tables"
down_revision = "001_add_document_source"
branch_labels = None
depends_on = None


def upgrade():
    visibility = sa.Enum("public", "private", "attorney_only", name="messagevisibility")
    visibility.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "conversation",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("participants", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "message",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("conversation_id", sa.String(length=36), sa.ForeignKey("conversation.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("agent.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("document_ids", sa.JSON(), nullable=True),
        sa.Column("reply_to_id", sa.String(length=36), sa.ForeignKey("message.id"), nullable=True),
        sa.Column("visibility", visibility, nullable=False, server_default="public"),
        sa.Column("vector_id", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_message_conversation_id", "message", ["conversation_id"])


def downgrade():
    op.drop_index("ix_message_conversation_id", table_name="message")
    op.drop_table("message")
    op.drop_table("conversation")
    sa.Enum(name="messagevisibility").drop(op.get_bind(), checkfirst=True)
