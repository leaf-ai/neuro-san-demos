"""Add source field to Document"""

from alembic import op
import sqlalchemy as sa

revision = "001_add_document_source"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    doc_source = sa.Enum("user", "opp_counsel", "court", name="documentsource")
    doc_source.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "document",
        sa.Column("source", doc_source, nullable=False, server_default="user"),
    )
    op.alter_column("document", "source", server_default=None)


def downgrade():
    op.drop_column("document", "source")
    sa.Enum(name="documentsource").drop(op.get_bind(), checkfirst=True)
