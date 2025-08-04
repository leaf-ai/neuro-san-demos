import pytest

from coded_tools.legal_discovery.fact_extractor import FactExtractor


@pytest.mark.slow
def test_fact_extraction_basic():
    extractor = FactExtractor()
    text = "On May 5, 2024, Alice signed a contract with Bob."
    facts = extractor.extract(text)
    assert len(facts) == 1
    fact = facts[0]
    assert "Alice" in fact["parties"]
    assert "Bob" in fact["parties"]
    assert any("May" in d for d in fact["dates"])
    assert "sign" in fact["actions"]
