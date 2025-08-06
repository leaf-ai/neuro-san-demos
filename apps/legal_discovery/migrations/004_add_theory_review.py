from apps.legal_discovery.database import db


def upgrade():
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE legal_theory ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'"))
        conn.execute(db.text("ALTER TABLE legal_theory ADD COLUMN review_comment TEXT"))


def downgrade():
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE legal_theory DROP COLUMN status"))
        conn.execute(db.text("ALTER TABLE legal_theory DROP COLUMN review_comment"))
