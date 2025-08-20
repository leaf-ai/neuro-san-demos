import logging

from apps.legal_discovery import database


class DummySession:
    def merge(self, entry):
        raise RuntimeError("merge fail")

    def commit(self):
        raise RuntimeError("commit fail")

    def rollback(self):
        raise RuntimeError("rollback fail")


def test_log_ingestion_failure_logs(monkeypatch, caplog):
    dummy = DummySession()
    monkeypatch.setattr(database.db, "session", dummy)
    with caplog.at_level(logging.ERROR):
        database.log_ingestion(
            case_id="c", path="p", doc_id="d", segment_hashes=[], status="ingested"
        )
    assert "failed to log ingestion" in caplog.text
    assert "failed to rollback ingestion log" in caplog.text
