from coded_tools.legal_discovery.ontology_loader import OntologyLoader


def test_loads_ontology_and_accesses_cause():
    loader = OntologyLoader()
    ontology = loader.load()
    assert "causes_of_action" in ontology
    cause = loader.get_cause("Breach of Contract")
    assert cause is not None
    assert "elements" in cause
    assert "defenses" in cause
