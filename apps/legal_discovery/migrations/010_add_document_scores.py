from alembic import op
import sqlalchemy as sa

revision = "010_add_document_scores"
down_revision = "009_add_document_versions"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("document") as batch:
        batch.add_column(sa.Column("probative_value", sa.Float(), nullable=True))
        batch.add_column(sa.Column("admissibility_risk", sa.Float(), nullable=True))
        batch.add_column(sa.Column("narrative_alignment", sa.Float(), nullable=True))
        batch.add_column(sa.Column("score_confidence", sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table("document") as batch:
        batch.drop_column("probative_value")
        batch.drop_column("admissibility_risk")
        batch.drop_column("narrative_alignment")
        batch.drop_column("score_confidence")
