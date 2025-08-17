"""Legal Discovery Tools with lazy imports to avoid heavy optional deps."""

from importlib import import_module
from typing import Any

__all__ = [
    "CaseManagementTools",
    "CodeEditor",
    "CommandPrompt",
    "CourtListenerClient",
    "CocounselAgent",
    "DocumentDrafter",
    "DocumentModifier",
    "DocumentProcessor",
    "DocumentFetcher",
    "FileManager",
    "ForensicTools",
    "KnowledgeGraphManager",
    "PresentationGenerator",
    "PretrialGenerator",
    "ResearchTools",
    "InternetSearch",
    "SubpoenaManager",
    "TaskTracker",
    "TimelineManager",
    "VectorDatabaseManager",
    "WebScraper",
    "GraphAnalyzer",
    "OntologyLoader",
    "FactExtractor",
    "LegalTheoryEngine",
    "PrivilegeDetector",
    "SanctionsRiskAnalyzer",
    "BatesNumberingService",
    "stamp_pdf",
    "DepositionPrep",
    "RetrievalChatAgent",
    "AutoDrafter",
    "TemplateLibrary",
    "NarrativeDiscrepancyDetector",
    "DocumentScorer",
]

_module_map = {
    "CaseManagementTools": "case_management_tools",
    "CodeEditor": "code_editor",
    "CommandPrompt": "command_prompt",
    "CourtListenerClient": "courtlistener_client",
    "CocounselAgent": "cocounsel_agent",
    "DocumentDrafter": "document_drafter",
    "DocumentModifier": "document_modifier",
    "DocumentProcessor": "document_processor",
    "DocumentFetcher": "document_fetcher",
    "FileManager": "file_manager",
    "ForensicTools": "forensic_tools",
    "KnowledgeGraphManager": "knowledge_graph_manager",
    "PresentationGenerator": "presentation_generator",
    "PretrialGenerator": "pretrial_generator",
    "ResearchTools": "research_tools",
    "InternetSearch": "internet_search",
    "SubpoenaManager": "subpoena_manager",
    "TaskTracker": "task_tracker",
    "TimelineManager": "timeline_manager",
    "VectorDatabaseManager": "vector_database_manager",
    "WebScraper": "web_scraper",
    "GraphAnalyzer": "graph_analyzer",
    "OntologyLoader": "ontology_loader",
    "FactExtractor": "fact_extractor",
    "LegalTheoryEngine": "legal_theory_engine",
    "PrivilegeDetector": "privilege_detector",
    "SanctionsRiskAnalyzer": "sanctions_risk_analyzer",
    "BatesNumberingService": "bates_numbering",
    "stamp_pdf": "bates_numbering",
    "DepositionPrep": "deposition_prep",
    "RetrievalChatAgent": "chat_agent",
    "AutoDrafter": "auto_drafter",
    "TemplateLibrary": "template_library",
    "NarrativeDiscrepancyDetector": "narrative_discrepancy_detector",
    "DocumentScorer": "document_scorer",
}


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    if name in _module_map:
        module = import_module(f".{_module_map[name]}", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
