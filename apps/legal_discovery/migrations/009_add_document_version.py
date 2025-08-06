from alembic import op
import sqlalchemy as sa

revision = "009_add_document_version"
down_revision = "008_add_narrative_discrepancy"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "document_version",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("document_id", sa.Integer, sa.ForeignKey("document.id"), nullable=False),
        sa.Column("bates_number", sa.String(100), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("agent.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("file_path", sa.String(255), nullable=False),
    )


def downgrade():
    op.drop_table("document_version")
