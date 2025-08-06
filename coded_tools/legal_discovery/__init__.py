"""Legal Discovery Tools"""

from .case_management_tools import CaseManagementTools
from .code_editor import CodeEditor
from .command_prompt import CommandPrompt
from .courtlistener_client import CourtListenerClient
from .cocounsel_agent import CocounselAgent
from .document_drafter import DocumentDrafter
from .document_modifier import DocumentModifier
from .document_processor import DocumentProcessor
from .document_fetcher import DocumentFetcher
from .file_manager import FileManager
from .forensic_tools import ForensicTools
from .knowledge_graph_manager import KnowledgeGraphManager
from .presentation_generator import PresentationGenerator
from .pretrial_generator import PretrialGenerator
from .research_tools import ResearchTools
from .internet_search import InternetSearch
from .subpoena_manager import SubpoenaManager
from .task_tracker import TaskTracker
from .timeline_manager import TimelineManager
from .vector_database_manager import VectorDatabaseManager
from .web_scraper import WebScraper
from .graph_analyzer import GraphAnalyzer
from .ontology_loader import OntologyLoader
from .fact_extractor import FactExtractor
from .legal_theory_engine import LegalTheoryEngine
from .privilege_detector import PrivilegeDetector
from .sanctions_risk_analyzer import SanctionsRiskAnalyzer
from .bates_numbering import BatesNumberingService, stamp_pdf
from .deposition_prep import DepositionPrep
from .chat_agent import RetrievalChatAgent
from .auto_drafter import AutoDrafter
from .template_library import TemplateLibrary
from .narrative_discrepancy_detector import NarrativeDiscrepancyDetector

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
]
