import atexit
import logging
import os
import queue
import re
import subprocess
import threading
import time
import hashlib
import json

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# pylint: disable=import-error
import schedule
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import send_file
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO

from apps.legal_discovery.legal_discovery import legal_discovery_thinker
from apps.legal_discovery.legal_discovery import (
    set_up_legal_discovery_assistant,
    tear_down_legal_discovery_assistant,
)


from more_itertools import chunked
from pyhocon import ConfigFactory

from apps.legal_discovery import settings
from apps.legal_discovery.database import db
from coded_tools.legal_discovery.deposition_prep import DepositionPrep
from apps.legal_discovery.models import (
    Case,
    Document,
    DocumentMetadata,
    LegalReference,
    TimelineEvent,
    CalendarEvent,
    LegalTheory,
    Fact,
    RedactionLog,
    RedactionAudit,
    Witness,
    DepositionQuestion,
    DepositionReviewLog,
)

# Configure logging before any other setup so early steps are captured
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

# Resolve project root relative to this file so Docker and local runs share paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ["AGENT_MANIFEST_FILE"] = os.environ.get(
    "AGENT_MANIFEST_FILE",
    os.path.join(BASE_DIR, "registries", "manifest.hocon"),
)
os.environ["AGENT_TOOL_PATH"] = os.environ.get(
    "AGENT_TOOL_PATH",
    os.path.join(BASE_DIR, "coded_tools"),
)
os.environ["AGENT_LLM_INFO_FILE"] = os.environ.get(
    "AGENT_LLM_INFO_FILE",
    os.path.join(BASE_DIR, "registries", "llm_config.hocon"),
)
# Ensure the React build exists so the dashboard can render
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
BUNDLE_PATH = os.path.join(STATIC_DIR, "bundle.js")
if not os.path.exists(BUNDLE_PATH):
    logging.info("No frontend bundle found; running npm build")
    subprocess.run(
        ["npm", "--prefix", os.path.dirname(__file__), "run", "build", "--silent"],
        check=True,
    )
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
# Allow the primary relational store to be configured at runtime. Default to
# SQLite for local development but override with an environment-provided
# PostgreSQL connection string when available so the application scales under
# concurrent load.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///legal_discovery.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
socketio = SocketIO(app)
executor = ThreadPoolExecutor(max_workers=int(os.environ.get("INGESTION_WORKERS", "4")))
atexit.register(executor.shutdown)
thread_started = False  # pylint: disable=invalid-name

app.logger.setLevel(logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")))

user_input_queue = queue.Queue()

# Shared agent session and worker thread are initialized asynchronously
legal_discovery_session = None
legal_discovery_thread = None


def _gather_upload_paths() -> list[str]:
    """Return a list of all files currently uploaded."""
    root = os.path.abspath("uploads")
    paths = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            paths.append(os.path.join(dirpath, fname))
    return paths


def _initialize_agent() -> None:

    """Set up the legal discovery assistant in a background thread."""
    global legal_discovery_session, legal_discovery_thread
    with app.app_context():
        app.logger.info("Setting up legal discovery assistant...")
        legal_discovery_session, legal_discovery_thread = set_up_legal_discovery_assistant(
            _gather_upload_paths()
        )
        app.logger.info("...legal discovery assistant set up.")


with app.app_context():
    db.create_all()
    if not Case.query.first():
        default_case = Case(name="Default Case")
        db.session.add(default_case)
        db.session.commit()

threading.Thread(target=_initialize_agent, daemon=True).start()


def reinitialize_legal_discovery_session() -> None:
    """Reload the agent session with the latest uploaded files."""
    global legal_discovery_session, legal_discovery_thread
    if legal_discovery_session is not None:
        tear_down_legal_discovery_assistant(legal_discovery_session)
    legal_discovery_session, legal_discovery_thread = set_up_legal_discovery_assistant(
        _gather_upload_paths()
    )
    app.logger.info("Legal discovery session reinitialized")


def legal_discovery_thinking_process():
    """Main permanent agent-calling loop."""
    with app.app_context():  # Manually push the application context
        global legal_discovery_thread  # pylint: disable=global-statement
        thoughts = "thought: hmm, let's see now..."
        while True:
            socketio.sleep(1)
            if legal_discovery_session is None:
                continue

            app.logger.debug("Calling legal_discovery_thinker...")
            thoughts, legal_discovery_thread = legal_discovery_thinker(
                legal_discovery_session, legal_discovery_thread, thoughts
            )
            app.logger.debug("...legal_discovery_thinker returned.")
            app.logger.debug(thoughts)

            # Separating thoughts and speeches
            # Assume 'thoughts' is the string returned by legal_discovery_thinker

            thoughts_to_emit = []
            speeches_to_emit = []

            # --- 1.  Slice the input into blocks ----------------------------------------
            #     Each block begins with  "thought:"  or  "say:"  and continues until
            #     the next block or the end of the string.
            pattern = re.compile(
                r"(?m)^(thought|say):[ \t]*(.*?)(?=^\s*(?:thought|say):|\Z)", re.S  # look-ahead  # dot = newline
            )

            for kind, raw in pattern.findall(thoughts):
                content = raw.lstrip()  # drop the leading spaces/newline after the prefix
                if not content:
                    continue

                if kind == "thought":
                    timestamp = datetime.now().strftime("[%I:%M:%S%p]").lower()
                    thoughts_to_emit.append(f"{timestamp} thought: {content}")
                else:  # kind == "say"
                    speeches_to_emit.append(content)

            # --- 2.  Emit the blocks -----------------------------------------------------
            if thoughts_to_emit:
                socketio.emit(
                    "update_thoughts",
                    {"data": "\n".join(thoughts_to_emit)},
                    namespace="/chat",
                )

            if speeches_to_emit:
                socketio.emit(
                    "update_speech",
                    {"data": "\n".join(speeches_to_emit)},
                    namespace="/chat",
                )

            timestamp = datetime.now().strftime("[%I:%M:%S%p]").lower()
            thoughts = f"\n{timestamp} user: " + "[Silence]"
            try:
                user_input = user_input_queue.get(timeout=0.1)
                if user_input:
                    thoughts = f"\n{timestamp} user: " + user_input
                if user_input == "exit":
                    break
            except queue.Empty:
                time.sleep(0.1)
                continue


@socketio.on("connect", namespace="/chat")
def on_connect():
    """Start background task on connect."""
    global thread_started  # pylint: disable=global-statement
    if not thread_started:
        thread_started = True
        # let socketio manage the green-thread
        socketio.start_background_task(legal_discovery_thinking_process)


@app.route("/api/settings", methods=["GET", "POST"])
def manage_settings():
    if request.method == "POST":
        data = request.get_json()
        settings.save_user_settings(data)
        return jsonify({"message": "Settings saved successfully"})
    else:
        user_settings = settings.get_user_settings()
        if user_settings:
            return jsonify(
                {
                    "courtlistener_api_key": user_settings.courtlistener_api_key,
                    "courtlistener_com_api_endpoint": user_settings.courtlistener_com_api_endpoint,
                    "california_codes_url": user_settings.california_codes_url,
                    "gemini_api_key": user_settings.gemini_api_key,
                    "google_api_endpoint": user_settings.google_api_endpoint,
                    "verifypdf_api_key": user_settings.verifypdf_api_key,
                    "verify_pdf_endpoint": user_settings.verify_pdf_endpoint,
                    "riza_key": user_settings.riza_key,
                    "neo4j_uri": user_settings.neo4j_uri,
                    "neo4j_username": user_settings.neo4j_username,
                    "neo4j_password": user_settings.neo4j_password,
                    "neo4j_database": user_settings.neo4j_database,
                    "aura_instance_id": user_settings.aura_instance_id,
                    "aura_instance_name": user_settings.aura_instance_name,
                    "gcp_project_id": user_settings.gcp_project_id,
                    "gcp_vertex_ai_data_store_id": user_settings.gcp_vertex_ai_data_store_id,
                    "gcp_vertex_ai_search_app": user_settings.gcp_vertex_ai_search_app,
                    "gcp_service_account_key": user_settings.gcp_service_account_key,
                }
            )
        return jsonify({})


@app.route("/api/settings/api-keys", methods=["GET", "POST"])
def manage_api_keys():
    """Manage extended API key settings."""
    return manage_settings()


import shutil

from flask import send_from_directory


from coded_tools.legal_discovery.forensic_tools import ForensicTools
from coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager
from coded_tools.legal_discovery.timeline_manager import TimelineManager
from coded_tools.legal_discovery.research_tools import ResearchTools
from coded_tools.legal_discovery.document_modifier import DocumentModifier
from coded_tools.legal_discovery.document_drafter import DocumentDrafter
from coded_tools.legal_discovery.document_processor import DocumentProcessor
from coded_tools.legal_discovery.fact_extractor import FactExtractor
from coded_tools.legal_discovery.privilege_detector import PrivilegeDetector
from coded_tools.legal_discovery.ontology_loader import OntologyLoader
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine
from coded_tools.legal_discovery.task_tracker import TaskTracker
from coded_tools.legal_discovery.vector_database_manager import VectorDatabaseManager
from coded_tools.legal_discovery.subpoena_manager import SubpoenaManager
from coded_tools.legal_discovery.presentation_generator import PresentationGenerator
from coded_tools.legal_discovery.graph_analyzer import GraphAnalyzer


# Allow hosting the corpus on an attached volume via UPLOAD_ROOT
UPLOAD_FOLDER = os.environ.get("UPLOAD_ROOT", os.path.join(BASE_DIR, "uploads"))
SECURE_FOLDER = os.path.join(UPLOAD_FOLDER, "_original")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SECURE_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECURE_FOLDER"] = SECURE_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "txt", "csv", "doc", "docx", "ppt", "pptx", "jpg", "jpeg", "png", "gif"}
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB

# Singleton task tracker instance for quick task management
task_tracker = TaskTracker()


def allowed_file(filename: str) -> bool:
    """Check if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def unique_filename(filename: str) -> str:
    """Return a filesystem-safe name that does not overwrite existing uploads."""
    base_dir = app.config["UPLOAD_FOLDER"]
    name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(base_dir, candidate)):
        candidate = f"{name}_{counter}{ext}"
        counter += 1
    return candidate


def chunked(items: list, size: int) -> list[list]:
    """Yield successive ``size``-sized chunks from ``items``."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def match_elements(text: str, ontology: dict) -> list[tuple[str, str]]:
    """Return (cause, element) pairs whose keywords appear in ``text``."""
    matches: list[tuple[str, str]] = []
    lower = text.lower()
    for cause, data in ontology.get("causes_of_action", {}).items():
        for element in data.get("elements", []):
            tokens = [t for t in element.lower().split() if len(t) > 3]
            if any(tok in lower for tok in tokens):
                matches.append((cause, element))
    return matches


def build_file_tree(directory: str, root_length: int, docs: dict[str, Document]) -> list:
    """Recursively build a file tree structure."""
    tree = []
    for entry in os.scandir(directory):
        if entry.name.startswith("_"):
            continue
        rel_path = entry.path[root_length:].lstrip(os.sep)
        node = {"path": rel_path, "name": entry.name}
        doc = docs.get(rel_path)
        if doc:
            node["privileged"] = doc.is_privileged
        if entry.is_dir():
            node["children"] = build_file_tree(entry.path, root_length, docs)
        tree.append(node)
    return sorted(tree, key=lambda x: (not x.get("children"), x["name"]))


@app.route("/api/files", methods=["GET"])
def list_files():
    """Return a hierarchical view of uploaded files."""
    root = os.path.abspath(app.config["UPLOAD_FOLDER"])
    if not os.path.exists(root):
        return jsonify({"status": "ok", "data": []})
    docs = {
        os.path.relpath(doc.file_path, root): doc
        for doc in Document.query.all()
    }
    data = build_file_tree(root, len(root), docs)
    return jsonify({"status": "ok", "data": data})


@app.route("/api/redaction/<int:doc_id>", methods=["POST"])
def review_redaction(doc_id: int):
    """Confirm or override a document's redaction status."""
    data = request.get_json() or {}
    action = data.get("action")
    reason = data.get("reason")
    reviewer = data.get("reviewer")
    doc = Document.query.get_or_404(doc_id)
    if action == "override":
        doc.is_privileged = False
        doc.is_redacted = False
        doc.needs_review = False
        orig = os.path.join(app.config["SECURE_FOLDER"], doc.name)
        try:
            shutil.copy(orig, doc.file_path)
        except OSError:
            pass
    elif action == "confirm":
        doc.needs_review = False
    else:
        return jsonify({"error": "Invalid action"}), 400
    db.session.add(
        RedactionAudit(
            document_id=doc.id, reviewer=reviewer, action=action, reason=reason
        )
    )
    db.session.commit()
    return jsonify({"status": "ok"})


@app.route("/api/agents", methods=["GET"])
def list_agents():
    """Return agent team names from the legal discovery registry."""
    config_path = os.path.join(BASE_DIR, "registries", "legal_discovery.hocon")
    cfg = ConfigFactory.parse_file(config_path)
    orchestrator = cfg.get("tools")[0]
    agents = [{"name": name} for name in orchestrator.get("tools", [])]
    return jsonify({"status": "ok", "data": agents})


@app.route("/api/topics", methods=["GET"])
def list_topics():
    """Return distinct legal theory topics from the database."""
    case_id = request.args.get("case_id")
    query = LegalTheory.query
    if case_id:
        query = query.filter_by(case_id=case_id)
    topics = query.with_entities(LegalTheory.theory_name).distinct().all()
    data = [{"label": name} for (name,) in topics]
    return jsonify({"status": "ok", "data": data})


@app.route("/api/calendar", methods=["GET", "POST", "DELETE"])
def calendar_events():
    """Manage calendar events for a case."""
    if request.method == "POST":
        data = request.get_json() or {}
        case_id = data.get("case_id")
        date = data.get("date")
        title = data.get("title")
        if not case_id or not date or not title:
            return jsonify({"error": "Missing case_id, date or title"}), 400
        event = CalendarEvent(
            case_id=case_id,
            title=title,
            event_date=datetime.fromisoformat(date),
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({"status": "ok", "id": event.id})

    if request.method == "DELETE":
        data = request.get_json() or {}
        event_id = data.get("id")
        if not event_id:
            return jsonify({"error": "Missing id"}), 400
        event = CalendarEvent.query.get(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        db.session.delete(event)
        db.session.commit()
        return jsonify({"status": "ok"})

    case_id = request.args.get("case_id")
    if not case_id:
        return jsonify({"status": "ok", "data": []})
    events = (
        CalendarEvent.query.filter_by(case_id=case_id)
        .order_by(CalendarEvent.event_date)
        .all()
    )
    data = [
        {"id": e.id, "date": e.event_date.strftime("%Y-%m-%d"), "title": e.title}
        for e in events
    ]
    return jsonify({"status": "ok", "data": data})


def _collect_paths(root: str) -> list:
    paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            paths.append(os.path.relpath(os.path.join(dirpath, f), root))
    return paths


def _categorize_name(name: str) -> str:
    name = name.lower()
    if any(k in name for k in ["complaint", "response", "petition"]):
        return "Pleadings"
    if "deposition" in name:
        return "Depositions"
    if any(k in name for k in ["contract", "agreement"]):
        return "Contracts"
    if "email" in name:
        return "Emails"
    if any(k in name for k in ["memo", "memorandum"]):
        return "Memos"
    return "Other"


def _paths_to_tree(paths: list) -> list:
    tree = {}
    for p in paths:
        parts = p.split(os.sep)
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node.setdefault("_files", []).append(parts[-1])

    def convert(d, prefix=""):
        items = []
        for name, val in sorted(d.items()):
            if name == "_files":
                for fname in val:
                    items.append({"name": fname, "path": os.path.join(prefix, fname)})
            else:
                items.append(
                    {
                        "name": name,
                        "path": os.path.join(prefix, name),
                        "children": convert(val, os.path.join(prefix, name)),
                    }
                )
        return items

    return convert(tree)


@app.route("/api/organized-files", methods=["GET"])
def organized_files():
    """Return files grouped into simple categories."""
    root = os.path.abspath(app.config["UPLOAD_FOLDER"])
    if not os.path.exists(root):
        return jsonify({"status": "ok", "data": {}})

    files = _collect_paths(root)
    categories = {}
    for path in files:
        cat = _categorize_name(os.path.basename(path))
        categories.setdefault(cat, []).append(path)

    data = {cat: _paths_to_tree(paths) for cat, paths in categories.items()}
    return jsonify({"status": "ok", "data": data})


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    """Serve a file from the uploads folder."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)


def cleanup_upload_folder(max_age_hours: int = 24) -> None:
    """Remove uploaded files older than ``max_age_hours``."""
    cutoff = time.time() - max_age_hours * 3600
    for root_dir, _, files in os.walk(app.config["UPLOAD_FOLDER"]):
        for name in files:
            path = os.path.join(root_dir, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except FileNotFoundError:
                continue


def ingest_document(
    original_path: str,
    redacted_path: str,
    doc_id: int,
    case_id: int,
    full_metadata: dict,
    chroma_metadata: dict,
) -> None:
    """Extract, vectorize, and relate a document in the background."""
    processor = DocumentProcessor()
    text = processor.extract_text(original_path) or ""
    detector = PrivilegeDetector()
    privileged, spans = detector.detect(text)
    doc = Document.query.get(doc_id)
    if privileged:
        keywords = [text[s.start : s.end] for s in spans]
        if original_path.lower().endswith(".pdf"):
            detector.redact_pdf(original_path, redacted_path, keywords)
            redacted_text = processor.extract_text(redacted_path) or ""
        else:
            redacted_text = detector.redact_text(text, spans)
            with open(redacted_path, "w", encoding="utf-8") as f:
                f.write(redacted_text)
        doc.is_privileged = True
        doc.is_redacted = True
        doc.needs_review = True
        for s in spans:
            db.session.add(
                RedactionLog(
                    document_id=doc_id, start=s.start, end=s.end, label=s.label
                )
            )
    else:
        shutil.copy(original_path, redacted_path)
        redacted_text = text
        doc.is_privileged = False
        doc.is_redacted = False
        doc.needs_review = False
    db.session.commit()

    VectorDatabaseManager().add_documents([redacted_text], [chroma_metadata], [str(doc_id)])
    kg = KnowledgeGraphManager()
    result = kg.run_query(
        "MERGE (c:Case {id: $id}) RETURN id(c) as cid", {"id": case_id}
    )
    case_node = result[0]["cid"] if result else None
    doc_node = kg.create_node("Document", full_metadata)
    if case_node:
        kg.create_relationship(case_node, doc_node, "HAS_DOCUMENT")

    extractor = FactExtractor()
    ontology = OntologyLoader().load()
    for fact in extractor.extract(redacted_text):
        fact_row = Fact(
            case_id=case_id,
            document_id=doc_id,
            text=fact["text"],
            parties=fact["parties"],
            dates=fact["dates"],
            actions=fact["actions"],
        )
        db.session.add(fact_row)
        fact_id = None
        if case_node or doc_node:
            fact_id = kg.add_fact(case_node, doc_node, fact)
        if fact_id is not None:
            for cause, element in match_elements(fact["text"], ontology):
                kg.link_fact_to_element(fact_id, cause, element)

    kg.close()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_TIMEOUT = 30  # seconds per file

@app.route("/api/upload", methods=["POST"])
def upload_files():
    upload_root = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_root, exist_ok=True)
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files provided"}), 400

    processed, skipped = [], []
    case = Case.query.first()
    case_id = case.id if case else 1

    def record_skip(name, reason):
        skipped.append(name)
        app.logger.warning(f"[SKIP] {name} — {reason}")
        with open("skipped_files.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().isoformat()}] {name} — {reason}\n")

    for batch_index, batch in enumerate([files[i:i + 10] for i in range(0, len(files), 10)]):
        app.logger.info(f"Starting batch {batch_index + 1}")
        batch_processed: list[str] = []
        futures: list[tuple] = []

        for file in batch:
            raw_name = os.path.normpath(file.filename)
            if not raw_name or not allowed_file(raw_name):
                record_skip(raw_name, "disallowed or blank filename")
                continue

            if getattr(file, "content_length", None) and file.content_length > MAX_FILE_SIZE:
                record_skip(raw_name, "file too large")
                continue

            hasher, total_read = hashlib.sha256(), 0
            start_time = time.time()
            try:
                for chunk in iter(lambda: file.stream.read(8192), b""):
                    hasher.update(chunk)
                    total_read += len(chunk)
                    if time.time() - start_time > MAX_TIMEOUT or total_read > MAX_FILE_SIZE:
                        raise TimeoutError("Exceeded time/size limit during hash")
                file.stream.seek(0)
            except Exception as exc:
                record_skip(raw_name, f"hashing error: {exc}")
                continue

            file_hash = hasher.hexdigest()
            if Document.query.filter_by(content_hash=file_hash).first():
                record_skip(raw_name, "duplicate hash")
                continue

            filename = unique_filename(raw_name)
            redacted_path = os.path.join(upload_root, filename)
            original_path = os.path.join(app.config["SECURE_FOLDER"], filename)
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            os.makedirs(os.path.dirname(redacted_path), exist_ok=True)
            try:
                file.save(original_path)
            except Exception as exc:
                record_skip(raw_name, f"save error: {exc}")
                continue

            doc = Document(case_id=case_id, name=filename, file_path=redacted_path, content_hash=file_hash)
            db.session.add(doc)
            db.session.flush()

            full_metadata = {
                "filename": filename,
                "path": redacted_path,
                "original_path": original_path,
                "case_id": case_id,
                "document_id": str(doc.id),
                "sha256": file_hash,
                "upload_time": str(time.time()),
            }
            chroma_metadata = {
                k: str(v)
                for k, v in full_metadata.items()
                if isinstance(v, (str, int, float, bool))
            }

            with open(redacted_path + ".meta.json", "w") as f:
                json.dump(full_metadata, f, indent=2)

            raw_meta = DocumentMetadata(document_id=doc.id, schema="raw", data=full_metadata)
            chroma_meta = DocumentMetadata(document_id=doc.id, schema="chroma", data=chroma_metadata)
            db.session.add_all([raw_meta, chroma_meta])
            future = executor.submit(
                ingest_document,
                original_path,
                redacted_path,
                doc.id,
                case_id,
                full_metadata,
                chroma_metadata,
            )
            futures.append((future, doc, raw_name, filename, redacted_path, raw_meta, chroma_meta))

        for future, doc, raw_name, filename, redacted_path, raw_meta, chroma_meta in futures:
            try:
                future.result(timeout=MAX_TIMEOUT)
            except TimeoutError:
                record_skip(raw_name, "ingestion timeout")
                db.session.delete(doc)
                db.session.delete(raw_meta)
                db.session.delete(chroma_meta)
                for ext in ("", ".meta.json"):
                    try:
                        os.remove(redacted_path + ext)
                    except OSError:
                        pass
            except Exception as exc:  # pragma: no cover - best effort
                record_skip(raw_name, f"ingestion error: {exc}")
                db.session.delete(doc)
                db.session.delete(raw_meta)
                db.session.delete(chroma_meta)
                for ext in ("", ".meta.json"):
                    try:
                        os.remove(redacted_path + ext)
                    except OSError:
                        pass
            else:
                processed.append(filename)
                batch_processed.append(filename)

        try:
            db.session.commit()
        except Exception as exc:  # pragma: no cover - best effort
            db.session.rollback()
            app.logger.error("Batch commit failed: %s", exc)

        try:
            VectorDatabaseManager().client.persist()
        except Exception:  # pragma: no cover - best effort
            app.logger.warning("Vector DB persist failed")

        if batch_processed:
            reinitialize_legal_discovery_session()
            user_input_queue.put(
                "process all files ingested within your scope and produce a basic overview and report."
            )

    return jsonify({"status": "ok", "processed": processed, "skipped": skipped})

@app.route("/api/export", methods=["GET"])
def export_files():
    shutil.make_archive("processed_files", "zip", UPLOAD_FOLDER)
    return send_from_directory(".", "processed_files.zip", as_attachment=True)


@app.route("/api/agents/forensic_analysis", methods=["POST"])
def forensic_analysis():
    data = request.get_json()
    file_path = data.get("file_path")
    analysis_type = data.get("analysis_type")

    if not file_path or not analysis_type:
        return jsonify({"error": "Missing file_path or analysis_type"}), 400

    forensic_tools = ForensicTools()

    if analysis_type == "authenticity":
        result = forensic_tools.analyze_document_authenticity(file_path)
    elif analysis_type == "financial":
        result = forensic_tools.financial_forensics(file_path)
    else:
        return jsonify({"error": "Invalid analysis_type"}), 400

    return jsonify({"result": result})


@app.route("/api/forensic/logs", methods=["GET"])
def forensic_logs():
    """Return forensic analysis logs if available."""
    log_path = os.path.join(app.config["UPLOAD_FOLDER"], "forensic.log")
    if not os.path.exists(log_path):
        return jsonify({"status": "ok", "data": []})
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    return jsonify({"status": "ok", "data": lines})


@app.route("/api/document/redact", methods=["POST"])
def redact_document():
    """Redact occurrences of text in a PDF using DocumentModifier."""
    data = request.get_json() or {}
    file_path = data.get("file_path")
    text = data.get("text")
    if not file_path or not text:
        return jsonify({"error": "Missing file_path or text"}), 400

    modifier = DocumentModifier()
    try:
        modifier.redact_text(file_path, text)
    except Exception as exc:  # pragma: no cover - filesystem errors
        return jsonify({"error": str(exc)}), 500
    return jsonify({"message": "File redacted", "output": f"{file_path}_redacted.pdf"})


@app.route("/api/document/stamp", methods=["POST"])
def bates_stamp_document():
    """Apply Bates numbering to a PDF."""
    data = request.get_json() or {}
    file_path = data.get("file_path")
    prefix = data.get("prefix", "BATES")
    if not file_path:
        return jsonify({"error": "Missing file_path"}), 400
    modifier = DocumentModifier()
    try:
        modifier.bates_stamp(file_path, prefix)
    except Exception as exc:  # pragma: no cover - filesystem errors
        return jsonify({"error": str(exc)}), 500
    return jsonify({"message": "File stamped", "output": f"{file_path}_stamped.pdf"})


@app.route("/api/document/draft", methods=["POST"])
def draft_document():
    """Create or update a DOCX document using DocumentDrafter."""
    data = request.get_json() or {}
    filepath = data.get("filepath")
    content = data.get("content", "")
    action = data.get("action", "create")
    level = int(data.get("level", 1))
    if not filepath:
        return jsonify({"error": "Missing filepath"}), 400
    drafter = DocumentDrafter()
    try:
        if action == "paragraph":
            drafter.add_paragraph(filepath, content)
        elif action == "heading":
            drafter.add_heading(filepath, content, level)
        else:
            drafter.create_document(filepath, content)
    except Exception as exc:  # pragma: no cover - file system errors
        return jsonify({"error": str(exc)}), 500
    return jsonify({"status": "ok", "output": filepath})


@app.route("/api/vector/add", methods=["POST"])
def vector_add_documents():
    """Add documents to the vector database."""
    data = request.get_json() or {}
    documents = data.get("documents")
    ids = data.get("ids")
    if not documents or not ids:
        return jsonify({"error": "Missing documents or ids"}), 400
    metadatas = data.get("metadatas") or [
        {"source": "api"} for _ in documents
    ]
    metadatas = [md if md else {"source": "api"} for md in metadatas]
    if len(metadatas) != len(documents):
        return jsonify({"error": "Invalid metadata length"}), 400
    manager = VectorDatabaseManager()
    manager.add_documents(documents, metadatas, ids)
    return jsonify({"status": "ok"})


@app.route("/api/vector/search", methods=["GET"])
def vector_search():
    """Query the vector database."""
    query = request.args.get("q")
    if not query:
        return jsonify({"status": "ok", "data": {}})
    manager = VectorDatabaseManager()
    result = manager.query([query], n_results=5)
    return jsonify({"status": "ok", "data": result})


@app.route("/api/vector/count", methods=["GET"])
def vector_count():
    """Return the document count in the vector database."""
    manager = VectorDatabaseManager()
    count = manager.get_document_count()
    return jsonify({"status": "ok", "data": count})


@app.route("/api/document/text", methods=["POST"])
def extract_document_text():
    """Extract text from a document using DocumentProcessor."""
    data = request.get_json() or {}
    file_path = data.get("file_path")
    if not file_path:
        return jsonify({"error": "Missing file_path"}), 400
    processor = DocumentProcessor()
    try:
        text = processor.extract_text(file_path)
    except Exception as exc:  # pragma: no cover - filesystem errors
        return jsonify({"error": str(exc)}), 500
    return jsonify({"status": "ok", "data": text})


@app.route("/api/tasks", methods=["GET", "POST", "DELETE"])
def manage_tasks():
    """Simple task tracker endpoints."""
    if request.method == "POST":
        data = request.get_json() or {}
        task = data.get("task")
        if not task:
            return jsonify({"error": "Missing task"}), 400
        msg = task_tracker.add_task(task)
        return jsonify({"status": "ok", "message": msg})
    if request.method == "DELETE":
        msg = task_tracker.clear_tasks()
        return jsonify({"status": "ok", "message": msg})

    tasks = task_tracker.list_tasks()
    return jsonify({"status": "ok", "data": tasks})


@app.route("/api/cases", methods=["GET", "POST", "DELETE"])
def manage_cases():
    """List, create or delete cases."""
    if request.method == "POST":
        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "Missing name"}), 400
        case = Case(name=name)
        db.session.add(case)
        db.session.commit()
        return jsonify({"status": "ok", "id": case.id})

    if request.method == "DELETE":
        data = request.get_json() or {}
        case_id = data.get("id")
        if not case_id:
            return jsonify({"error": "Missing id"}), 400
        case = Case.query.get(case_id)
        if not case:
            return jsonify({"error": "Case not found"}), 404
        Document.query.filter_by(case_id=case_id).delete()
        TimelineEvent.query.filter_by(case_id=case_id).delete()
        LegalReference.query.filter_by(case_id=case_id).delete()
        db.session.delete(case)
        db.session.commit()
        return jsonify({"status": "ok"})

    cases = Case.query.all()
    data = [{"id": c.id, "name": c.name} for c in cases]
    return jsonify({"status": "ok", "data": data})


@app.route("/api/witnesses", methods=["GET", "POST"])
def manage_witnesses():
    if request.method == "POST":
        data = request.get_json() or {}
        name = data.get("name")
        case_id = data.get("case_id")
        if not name:
            return jsonify({"error": "Missing name"}), 400
        witness = Witness(name=name, role=data.get("role"), associated_case=case_id)
        db.session.add(witness)
        db.session.commit()
        return jsonify({"status": "ok", "id": witness.id})
    case_id = request.args.get("case_id", type=int)
    query = Witness.query
    if case_id:
        query = query.filter_by(associated_case=case_id)
    witnesses = query.all()
    data = [{"id": w.id, "name": w.name} for w in witnesses]
    return jsonify({"status": "ok", "data": data})


@app.route("/api/deposition/questions", methods=["POST"])
def generate_deposition_questions():
    data = request.get_json() or {}
    witness_id = data.get("witness_id")
    include_privileged = data.get("include_privileged", False)
    if not witness_id:
        return jsonify({"error": "Missing witness_id"}), 400
    questions = DepositionPrep.generate_questions(
        witness_id, include_privileged=include_privileged
    )
    return jsonify({"status": "ok", "data": questions})


@app.route("/api/deposition/questions/<int:question_id>/flag", methods=["POST"])
def flag_deposition_question(question_id: int):
    DepositionPrep.flag_question(question_id)
    return jsonify({"status": "ok"})


@app.route("/api/deposition/export/<int:witness_id>", methods=["GET"])
def export_deposition_questions(witness_id: int):
    fmt = request.args.get("format", "docx")
    os.makedirs("exports", exist_ok=True)
    path = os.path.join("exports", f"deposition_{witness_id}.{fmt}")
    DepositionPrep.export_questions(witness_id, path)
    return send_file(path, as_attachment=True)


@app.route("/api/subpoena/draft", methods=["POST"])
def draft_subpoena():
    """Draft a subpoena document using SubpoenaManager."""
    data = request.get_json() or {}
    file_path = data.get("file_path")
    content = data.get("content")
    if not file_path or not content:
        return jsonify({"error": "Missing file_path or content"}), 400
    mgr = SubpoenaManager()
    try:
        mgr.draft_subpoena_document(file_path, content)
    except Exception as exc:  # pragma: no cover - file system errors
        return jsonify({"error": str(exc)}), 500
    return jsonify({"status": "ok", "output": file_path})


@app.route("/api/presentation", methods=["POST"])
def create_presentation():
    """Create or update a PowerPoint presentation."""
    data = request.get_json() or {}
    filepath = data.get("filepath")
    slides = data.get("slides", [])
    if not filepath or not isinstance(slides, list):
        return jsonify({"error": "Missing filepath or slides"}), 400
    gen = PresentationGenerator()
    try:
        gen.create_presentation(filepath)
        for slide in slides:
            title = slide.get("title", "")
            content = slide.get("content", "")
            gen.add_slide(filepath, title, content)
    except Exception as exc:  # pragma: no cover - file system errors
        return jsonify({"error": str(exc)}), 500
    return jsonify({"status": "ok", "output": filepath})


@app.route("/api/progress", methods=["GET"])
def progress_status():
    """Return basic progress metrics."""
    root = app.config["UPLOAD_FOLDER"]
    upload_count = 0
    if os.path.exists(root):
        upload_count = sum(len(f) for _, _, f in os.walk(root))
    data = {"uploaded_files": upload_count}
    return jsonify({"status": "ok", "data": data})


@app.route("/api/metrics", methods=["GET"])
def aggregated_metrics():
    """Return combined counts for dashboard metrics."""
    root = app.config["UPLOAD_FOLDER"]
    upload_count = 0
    if os.path.exists(root):
        upload_count = sum(len(f) for _, _, f in os.walk(root))

    vector_count = 0
    try:
        vector_count = VectorDatabaseManager().get_document_count()
    except Exception:  # pragma: no cover - optional dependency may fail
        vector_count = 0

    graph_count = 0
    try:
        kg_manager = KnowledgeGraphManager()
        result = kg_manager.run_query("MATCH (n) RETURN count(n) AS count")
        graph_count = result[0]["count"] if result else 0
        kg_manager.close()
    except Exception:  # pragma: no cover - database may be unavailable
        graph_count = 0

    task_count = len(task_tracker.list_tasks())

    case_count = Case.query.count()

    log_path = os.path.join(root, "forensic.log")
    log_count = 0
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            log_count = len(f.read().splitlines())

    data = {
        "uploaded_files": upload_count,
        "vector_docs": vector_count,
        "graph_nodes": graph_count,
        "task_count": task_count,
        "forensic_logs": log_count,
        "case_count": case_count,
    }
    return jsonify({"status": "ok", "data": data})


@app.route("/api/graph/export", methods=["GET"])
def export_graph():
    kg_manager = KnowledgeGraphManager()
    output_path = kg_manager.export_graph()
    kg_manager.close()
    return send_from_directory(".", output_path, as_attachment=False)


@app.route("/api/graph", methods=["GET"])
def get_graph():
    subnet = request.args.get("subnet", "")
    kg_manager = KnowledgeGraphManager()
    try:
        nodes, edges = kg_manager.get_subgraph(subnet) if subnet else kg_manager.get_subgraph("*")
    except Exception:
        nodes, edges = [], []
    kg_manager.close()
    return jsonify({"status": "ok", "data": {"nodes": nodes, "edges": edges}})


@app.route("/api/graph/analyze", methods=["GET"])
def analyze_graph():
    """Return centrality analysis of the knowledge graph."""
    subnet = request.args.get("subnet", "*")
    analyzer = GraphAnalyzer()
    try:
        results = analyzer.analyze_centrality(subnet)
        user_input_queue.put(
            "Provide insights on the most connected entities in the case graph."
        )
    except Exception as exc:  # pragma: no cover - optional analysis may fail
        app.logger.error("Graph analysis failed: %s", exc)
        return jsonify({"error": str(exc)}), 500
    return jsonify({"status": "ok", "data": results})


@app.route("/api/graph/cypher", methods=["POST"])
def run_cypher_query():
    """Execute an arbitrary Cypher query against the knowledge graph."""
    data = request.get_json(force=True) or {}
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "missing query"}), 400
    kg = KnowledgeGraphManager()
    try:
        results = kg.run_query(query)
    except Exception as exc:  # pragma: no cover - user queries may fail
        kg.close()
        return jsonify({"error": str(exc)}), 400
    kg.close()
    return jsonify({"status": "ok", "data": results})


def _get_file_excerpt(case_id: str, length: int = 400) -> str | None:
    """Return a short excerpt from the first document for the case."""
    doc = Document.query.filter_by(case_id=case_id).first()
    if not doc or not doc.file_path:
        return None
    try:
        with open(doc.file_path, "r", errors="ignore") as f:
            return f.read(length)
    except Exception:  # pragma: no cover - optional file may be missing
        return None


@app.route("/api/timeline/export", methods=["POST"])
def export_timeline():
    data = request.get_json()
    timeline_id = data.get("timeline_id")

    if not timeline_id:
        return jsonify({"error": "Missing timeline_id"}), 400

    timeline_manager = TimelineManager()
    events = TimelineEvent.query.filter_by(case_id=timeline_id).order_by(TimelineEvent.event_date).all()

    timeline_items = []
    for event in events:
        citation = None
        ref = LegalReference.query.filter_by(case_id=event.case_id).first()
        if ref:
            citation = ref.source_url
        excerpt = _get_file_excerpt(event.case_id)
        timeline_items.append(
            {
                "content": event.description,
                "start": event.event_date.strftime("%Y-%m-%d"),
                "citation": citation,
                "excerpt": excerpt,
            }
        )

    html = timeline_manager.render_timeline(timeline_items)
    timeline_manager.close()
    return html


@app.route("/api/timeline", methods=["GET"])
def get_timeline():
    query = request.args.get("query")
    if not query:
        return jsonify({"status": "ok", "data": []})

    events = (
        TimelineEvent.query.filter_by(case_id=query)
        .order_by(TimelineEvent.event_date)
        .all()
    )

    data = []
    for event in events:
        citation = None
        ref = LegalReference.query.filter_by(case_id=event.case_id).first()
        if ref:
            citation = ref.source_url
        excerpt = _get_file_excerpt(event.case_id)
        data.append(
            {
                "id": event.id,
                "date": event.event_date.strftime("%Y-%m-%d"),
                "description": event.description,
                "citation": citation,
                "excerpt": excerpt,
            }
        )

    return jsonify({"status": "ok", "data": data})


@app.route("/api/research", methods=["GET"])
def research():
    query = request.args.get("query")
    source = request.args.get("source", "all")
    tool = ResearchTools()
    results = tool.search(query, source) if query else []
    return jsonify({"status": "ok", "data": results})


@app.route("/api/theories/suggest", methods=["GET"])
def suggest_theories():
    """Return ranked legal theory candidates."""
    engine = LegalTheoryEngine()
    theories = engine.suggest_theories()
    engine.close()
    return jsonify({"status": "ok", "theories": theories})


@app.route("/api/query", methods=["POST"])
def query_agent():
    data = request.get_json() or {}
    text = data.get("text")
    if text:
        user_input_queue.put(text)
    return jsonify({"status": "ok"})


@app.route("/api/export/report", methods=["POST"])
def export_report():
    data = request.get_json() or {}
    rpt_type = data.get("type")
    if rpt_type == "timeline":
        return export_timeline()
    elif rpt_type == "files":
        return export_files()
    elif rpt_type == "graph":
        return export_graph()
    else:
        return jsonify({"error": "Invalid type"}), 400


@app.route("/")
def index():
    """Serve the React dashboard by default."""
    return render_template("dashboard.html")


@app.route("/dashboard")
def dashboard():
    """Return the dashboard UI."""
    return render_template("dashboard.html")


@socketio.on("user_input", namespace="/chat")
def handle_user_input(json, *_):
    """
    Handles user input.

    :param json: A json object
    """
    user_input = json["data"]
    user_input_queue.put(user_input)
    socketio.emit("update_user_input", {"data": user_input}, namespace="/chat")


def cleanup():
    """Tear things down on exit."""
    app.logger.info("Bye!")
    if legal_discovery_session is not None:
        tear_down_legal_discovery_assistant(legal_discovery_session)
    socketio.stop()


@app.route("/shutdown")
def shutdown():
    """Shut down process."""
    cleanup()
    return "Capture ended"


@app.after_request
def add_header(response):
    """Add the header."""
    response.headers["Cache-Control"] = "no-store"
    return response


def run_scheduled_tasks():
    """Run the scheduled tasks."""
    while True:
        schedule.run_pending()
        time.sleep(1)


# Register the cleanup function
atexit.register(cleanup)

# Setup and start scheduled maintenance tasks
schedule.every().day.at("00:00").do(cleanup_upload_folder)
socketio.start_background_task(run_scheduled_tasks)

if __name__ == "__main__":
    app.logger.info("Starting Flask server...")
    with app.app_context():
        db.create_all()
    socketio.run(
        app,
        debug=False,
        host="0.0.0.0",
        port=5001,
        allow_unsafe_werkzeug=True,
        log_output=True,
        use_reloader=False,
    )
