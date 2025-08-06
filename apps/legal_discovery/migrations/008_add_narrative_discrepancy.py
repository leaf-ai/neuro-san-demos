from alembic import op
import sqlalchemy as sa

revision = "008_add_narrative_discrepancy"
down_revision = "007_add_message_audit_log"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "narrative_discrepancy",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("opposing_doc_id", sa.Integer, sa.ForeignKey("document.id"), nullable=False),
        sa.Column("user_doc_id", sa.Integer, sa.ForeignKey("document.id"), nullable=False),
        sa.Column("conflicting_claim", sa.Text(), nullable=False),
        sa.Column("evidence_excerpt", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("legal_theory_id", sa.Integer, sa.ForeignKey("legal_theory.id"), nullable=True),
        sa.Column("calendar_event_id", sa.Integer, sa.ForeignKey("calendar_event.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("narrative_discrepancy")
