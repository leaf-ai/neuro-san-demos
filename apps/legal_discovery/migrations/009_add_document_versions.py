from alembic import op
import sqlalchemy as sa

revision = "009_add_document_versions"
down_revision = "008_add_narrative_discrepancy"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "document_version",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("document_id", sa.Integer, sa.ForeignKey("document.id"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("bates_number", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("agent.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("document_version")
