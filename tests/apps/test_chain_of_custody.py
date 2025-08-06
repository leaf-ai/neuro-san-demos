from flask import Flask, jsonify, request

from apps.legal_discovery.database import db
from apps.legal_discovery.chain_logger import log_event
from apps.legal_discovery.models import (
    Case,
    Document,
    ChainEventType,
    ChainOfCustodyLog,
    DocumentSource,
)


def _setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    db.init_app(app)

    @app.route("/api/chain")
    def chain_api():
        doc_id = request.args.get("document_id", type=int)
        if not doc_id:
            return jsonify({"error": "Missing document_id"}), 400
        entries = (
            ChainOfCustodyLog.query.filter_by(document_id=doc_id)
            .order_by(ChainOfCustodyLog.timestamp)
            .all()
        )
        return jsonify(
            {
                "document_id": doc_id,
                "events": [
                    {
                        "type": e.event_type.value,
                        "timestamp": e.timestamp.isoformat(),
                        "user_id": e.user_id,
                        "metadata": e.event_metadata,
                        "signature_hash": e.signature_hash,
                    }
                    for e in entries
                ],
            }
        )

    return app


def test_chain_logger_and_api(tmp_path):
    app = _setup_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        case = Case(name="Case")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="d1",
            file_path=str(tmp_path / "d1.pdf"),
            sha256="deadbeef",
            source=DocumentSource.USER,
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

        log_event(doc_id, ChainEventType.INGESTED, user_id=1)
        log_event(doc_id, ChainEventType.REDACTED, user_id=2)
        log_event(doc_id, ChainEventType.STAMPED, user_id=3)
        log_event(doc_id, ChainEventType.EXPORTED, user_id=4)

    client = app.test_client()
    res = client.get(f"/api/chain?document_id={doc_id}")
    assert res.status_code == 200
    events = res.json["events"]
    assert [e["type"] for e in events] == [
        "INGESTED",
        "REDACTED",
        "STAMPED",
        "EXPORTED",
    ]
    for e, uid in zip(events, [1, 2, 3, 4]):
        assert e["user_id"] == uid
        assert len(e["signature_hash"]) == 64

