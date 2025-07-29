"""Legal Discovery Tools"""

from .case_management_tools import CaseManagementTools
from .code_editor import CodeEditor
from .courtlistener_client import CourtListenerClient
from .document_drafter import DocumentDrafter
from .document_modifier import DocumentModifier
from .document_processor import DocumentProcessor
from .file_manager import FileManager
from .forensic_tools import ForensicTools
from .knowledge_graph_manager import KnowledgeGraphManager
from .presentation_generator import PresentationGenerator
from .research_tools import ResearchTools
from .subpoena_manager import SubpoenaManager
from .task_tracker import TaskTracker
from .timeline_manager import TimelineManager
from .vector_database_manager import VectorDatabaseManager
from .web_scraper import WebScraper
from .graph_analyzer import GraphAnalyzer

__all__ = [
    "CaseManagementTools",
    "CodeEditor",
    "CourtListenerClient",
    "DocumentDrafter",
    "DocumentModifier",
    "DocumentProcessor",
    "FileManager",
    "ForensicTools",
    "KnowledgeGraphManager",
    "PresentationGenerator",
    "ResearchTools",
    "SubpoenaManager",
    "TaskTracker",
    "TimelineManager",
    "VectorDatabaseManager",
    "WebScraper",
    "GraphAnalyzer",
]
