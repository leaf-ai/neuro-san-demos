from coded_tools.legal_discovery.ontology_loader import OntologyLoader


def test_loads_ontology_and_accesses_cause():
    loader = OntologyLoader()
    ontology = loader.load()
    assert "causes_of_action" in ontology
    cause = loader.get_cause("Breach of Contract")
    assert cause is not None
    assert "elements" in cause
    assert "defenses" in cause


def test_defenses_indicators_and_missing_cause():
    loader = OntologyLoader()
    fraud = loader.get_cause("Fraud")
    assert "defenses" in fraud and "Truth" in fraud["defenses"]
    assert "indicators" in fraud and "false statement" in fraud["indicators"]
    assert loader.get_cause("Nonexistent") is None

def test_loader_handles_additional_causes():
    loader = OntologyLoader()
    negligence = loader.get_cause("Negligence")
    assert negligence is not None
    assert "Breach" in negligence["elements"]

