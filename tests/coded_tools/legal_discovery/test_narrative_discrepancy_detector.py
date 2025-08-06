import os

import pytest

from coded_tools.legal_discovery.narrative_discrepancy_detector import (
    NarrativeDiscrepancyDetector,
)


@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Gemini API key required")
def test_nli_returns_label_and_confidence():
    detector = NarrativeDiscrepancyDetector()
    label, confidence = detector._nli("The sky is blue.", "The sky is green.")
    assert label in {"CONTRADICTION", "ENTAILMENT", "NEUTRAL"}
    assert 0.0 <= confidence <= 1.0
