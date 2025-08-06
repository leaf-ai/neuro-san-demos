from alembic import op
import sqlalchemy as sa

revision = "010_add_timeline_links"
down_revision = "009_add_document_versions"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("timeline_event", sa.Column("links", sa.JSON(), nullable=True))

def downgrade():
    op.drop_column("timeline_event", "links")
