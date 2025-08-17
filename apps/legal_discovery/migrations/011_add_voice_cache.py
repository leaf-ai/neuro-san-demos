"""Add voice cache table"""

from alembic import op
import sqlalchemy as sa

revision = "011_add_voice_cache"
down_revision = ("010_add_timeline_links", "010_add_document_scores")
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "voice_cache",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("audio", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("text", "model", name="uix_voice_cache_text_model"),
    )


def downgrade():
    op.drop_table("voice_cache")

