from apps.legal_discovery.database import db


def upgrade():
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE document ADD COLUMN exhibit_order INTEGER NOT NULL DEFAULT 0"))


def downgrade():
    with db.engine.connect() as conn:
        conn.execute(db.text("ALTER TABLE document DROP COLUMN exhibit_order"))
