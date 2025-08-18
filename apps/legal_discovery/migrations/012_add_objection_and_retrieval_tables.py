from alembic import op
import sqlalchemy as sa

revision = "012_add_objection_and_retrieval_tables"
down_revision = "011_add_voice_cache"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "retrieval_traces",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("trace_id", sa.String(length=40), nullable=False),
        sa.Column("case_id", sa.String(length=64), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("graph_weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("dense_weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("timings", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_retrieval_traces_trace_id", "retrieval_traces", ["trace_id"]
    )

    op.create_table(
        "objection_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("segment_id", sa.String(), nullable=True),
        sa.Column("trace_id", sa.String(length=40), nullable=True),
        sa.Column("ts", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("ground", sa.String(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("extracted_phrase", sa.String(), nullable=True),
        sa.Column("suggested_cures", sa.JSON(), nullable=True),
        sa.Column("refs", sa.JSON(), nullable=True),
        sa.Column("path", sa.JSON(), nullable=True),
        sa.Column("action_taken", sa.String(), nullable=True),
        sa.Column("outcome", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_objection_events_session_id", "objection_events", ["session_id"]
    )
    op.create_index(
        "ix_objection_events_segment_id", "objection_events", ["segment_id"]
    )
    op.create_index(
        "ix_objection_events_trace_id", "objection_events", ["trace_id"]
    )

    op.create_table(
        "objection_resolutions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "event_id",
            sa.String(),
            sa.ForeignKey("objection_events.id"),
            nullable=True,
        ),
        sa.Column("chosen_cure", sa.String(), nullable=True),
        sa.Column("ts", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_objection_resolutions_event_id", "objection_resolutions", ["event_id"]
    )


def downgrade():
    op.drop_index(
        "ix_objection_resolutions_event_id", table_name="objection_resolutions"
    )
    op.drop_table("objection_resolutions")
    op.drop_index(
        "ix_objection_events_trace_id", table_name="objection_events"
    )
    op.drop_index(
        "ix_objection_events_segment_id", table_name="objection_events"
    )
    op.drop_index(
        "ix_objection_events_session_id", table_name="objection_events"
    )
    op.drop_table("objection_events")
    op.drop_index(
        "ix_retrieval_traces_trace_id", table_name="retrieval_traces"
    )
    op.drop_table("retrieval_traces")
