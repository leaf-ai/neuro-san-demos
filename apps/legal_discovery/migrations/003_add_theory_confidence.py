from alembic import op
import sqlalchemy as sa

revision = "003_add_theory_confidence"
down_revision = "002_add_chat_tables"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "theory_confidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("legal_theory_id", sa.Integer(), sa.ForeignKey("legal_theory.id"), nullable=False),
        sa.Column("fact_id", sa.Integer(), sa.ForeignKey("fact.id"), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_team", sa.String(length=100), nullable=False, server_default="unknown"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_theory_confidence_range"),
    )
    op.alter_column("theory_confidence", "source_team", server_default=None)
    op.create_index("ix_theory_confidence_theory_fact", "theory_confidence", ["legal_theory_id", "fact_id"], unique=True)


def downgrade():
    op.drop_index("ix_theory_confidence_theory_fact", table_name="theory_confidence")
    op.drop_table("theory_confidence")
