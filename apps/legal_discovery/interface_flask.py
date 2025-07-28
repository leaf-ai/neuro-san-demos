import atexit
import logging
import os
import queue
import re
import time
from datetime import datetime

# pylint: disable=import-error
import schedule
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO

from apps.legal_discovery.legal_discovery import legal_discovery_thinker
from apps.legal_discovery.legal_discovery import (
    set_up_legal_discovery_assistant,
    tear_down_legal_discovery_assistant,
)

from . import settings
from .database import db
from .models import Case, Document, LegalReference, TimelineEvent
from .models import LegalReference, TimelineEvent, Document

os.environ["AGENT_MANIFEST_FILE"] = os.environ.get(
    "AGENT_MANIFEST_FILE",
    "registries/legal_discovery.hocon",
)
os.environ["AGENT_TOOL_PATH"] = os.environ.get("AGENT_TOOL_PATH", "coded_tools")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///legal_discovery.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
socketio = SocketIO(app)
thread_started = False  # pylint: disable=invalid-name

# Configure logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
app.logger.setLevel(logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")))

user_input_queue = queue.Queue()


def _gather_upload_paths() -> list[str]:
    """Return a list of all files currently uploaded."""
    root = os.path.abspath("uploads")
    paths = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            paths.append(os.path.join(dirpath, fname))
    return paths

with app.app_context():

    db.create_all()
    if not Case.query.first():
        default_case = Case(name="Default Case")
        db.session.add(default_case)
        db.session.commit()

    app.logger.info("Setting up legal discovery assistant...")
    legal_discovery_session, legal_discovery_thread = set_up_legal_discovery_assistant(_gather_upload_paths())
    app.logger.info("...legal discovery assistant set up.")


def reinitialize_legal_discovery_session() -> None:
    """Reload the agent session with the latest uploaded files."""
    global legal_discovery_session, legal_discovery_thread
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
from coded_tools.legal_discovery.document_processor import DocumentProcessor
from coded_tools.legal_discovery.task_tracker import TaskTracker
from coded_tools.legal_discovery.vector_database_manager import (
    VectorDatabaseManager,
)
from coded_tools.legal_discovery.subpoena_manager import SubpoenaManager
from coded_tools.legal_discovery.presentation_generator import PresentationGenerator


UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "txt", "csv", "doc", "docx", "ppt", "pptx", "jpg", "jpeg", "png", "gif"}

# Singleton task tracker instance for quick task management
task_tracker = TaskTracker()


def allowed_file(filename: str) -> bool:
    """Check if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_file_tree(directory: str, root_length: int) -> list:
    """Recursively build a file tree structure."""
    tree = []
    for entry in os.scandir(directory):
        rel_path = entry.path[root_length:].lstrip(os.sep)
        node = {"path": rel_path, "name": entry.name}
        if entry.is_dir():
            node["children"] = build_file_tree(entry.path, root_length)
        tree.append(node)
    return sorted(tree, key=lambda x: (not x.get("children"), x["name"]))


@app.route("/api/files", methods=["GET"])
def list_files():
    """Return a hierarchical view of uploaded files."""
    root = os.path.abspath(app.config["UPLOAD_FOLDER"])
    if not os.path.exists(root):
        return jsonify({"status": "ok", "data": []})
    data = build_file_tree(root, len(root))
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


@app.route("/api/upload", methods=["POST"])
def upload_files():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files part"}), 400

    with app.app_context():
        case = Case.query.first()
        case_id = case.id if case else 1

        for file in files:
            if file.filename == "":
                continue
            filename = secure_filename(os.path.normpath(file.filename))
            if filename.startswith("..") or not allowed_file(filename):
                continue

            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)

            # store document record
            doc = Document(case_id=case_id, name=filename, file_path=save_path)
            db.session.add(doc)
            db.session.commit()

            # extract text and add to vector DB
            try:
                processor = DocumentProcessor()
                text = processor.extract_text(save_path)
                VectorDatabaseManager().add_documents([text], [{}], [str(doc.id)])
            except Exception as exc:  # pragma: no cover - best effort
                app.logger.error("Ingestion failed for %s: %s", save_path, exc)

    # Reload session metadata so new files are visible to the agent network
    reinitialize_legal_discovery_session()


            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)

            # store document record
            doc = Document(case_id=case_id, name=filename, file_path=save_path)
            db.session.add(doc)
            db.session.commit()

            # extract text and add to vector DB
            try:
                processor = DocumentProcessor()
                text = processor.extract_text(save_path)
                VectorDatabaseManager().add_documents([text], [{}], [str(doc.id)])
            except Exception as exc:  # pragma: no cover - best effort
                app.logger.error("Ingestion failed for %s: %s", save_path, exc)

    user_input_queue.put(
        "process all files ingested within your scope and produce a basic overview and report."
    )
    return jsonify({"message": "Files uploaded and processing started"})


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


@app.route("/api/vector/add", methods=["POST"])
def vector_add_documents():
    """Add documents to the vector database."""
    data = request.get_json() or {}
    documents = data.get("documents")
    ids = data.get("ids")
    metadatas = data.get("metadatas", [{} for _ in (documents or [])])
    if not documents or not ids:
        return jsonify({"error": "Missing documents or ids"}), 400
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
