import atexit
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
from flask_socketio import SocketIO

from apps.legal_discovery.legal_discovery import legal_discovery_thinker
from apps.legal_discovery.legal_discovery import set_up_legal_discovery_assistant
from apps.legal_discovery.legal_discovery import tear_down_legal_discovery_assistant

from . import settings
from .database import db

os.environ["AGENT_MANIFEST_FILE"] = "registries/manifest.hocon"
os.environ["AGENT_TOOL_PATH"] = "coded_tools"
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///legal_discovery.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
socketio = SocketIO(app)
thread_started = False  # pylint: disable=invalid-name

user_input_queue = queue.Queue()

legal_discovery_session, legal_discovery_thread = set_up_legal_discovery_assistant()


def legal_discovery_thinking_process():
    """Main permanent agent-calling loop."""
    with app.app_context():  # Manually push the application context
        global legal_discovery_thread  # pylint: disable=global-statement
        thoughts = "thought: hmm, let's see now..."
        while True:
            socketio.sleep(1)

            thoughts, legal_discovery_thread = legal_discovery_thinker(
                legal_discovery_session, legal_discovery_thread, thoughts
            )
            print(thoughts)

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
                    "gemini_api_key": user_settings.gemini_api_key,
                    "california_codes_url": user_settings.california_codes_url,
                }
            )
        return jsonify({})


import shutil

from flask import send_from_directory

from .coded_tools.legal_discovery.forensic_tools import ForensicTools
from .coded_tools.legal_discovery.knowledge_graph_manager import KnowledgeGraphManager
from .coded_tools.legal_discovery.timeline_manager import TimelineManager

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/api/upload", methods=["POST"])
def upload_files():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files part"}), 400

    for file in files:
        if file.filename == "":
            continue
        # The filename from the browser includes the relative path
        filename = file.filename
        # Sanitize the filename to prevent directory traversal attacks
        filename = os.path.normpath(filename)
        if filename.startswith(".."):
            continue

        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        file.save(save_path)

    return jsonify({"message": "Files uploaded successfully"})


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


@app.route("/api/graph/export", methods=["GET"])
def export_graph():
    kg_manager = KnowledgeGraphManager()
    output_path = kg_manager.export_graph()
    kg_manager.close()
    return send_from_directory(".", output_path, as_attachment=False)


@app.route("/api/timeline/export", methods=["POST"])
def export_timeline():
    data = request.get_json()
    timeline_id = data.get("timeline_id")

    if not timeline_id:
        return jsonify({"error": "Missing timeline_id"}), 400

    timeline_manager = TimelineManager()
    # This is a placeholder for getting the timeline data from the database
    # In a real app, you would fetch this from the database
    timeline_items = [
        {"content": "Event 1", "start": "2024-01-01", "citation": "https://www.courtlistener.com"},
        {"content": "Event 2", "start": "2024-01-15", "citation": "https://leginfo.legislature.ca.gov/"},
    ]

    html = timeline_manager.render_timeline(timeline_items)

    # In a real app, you would save this to a file and provide a download link
    return html


@app.route("/")
def index():
    """Return the html."""
    return render_template("index.html")


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
    print("Bye!")
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=False, port=5001, allow_unsafe_werkzeug=True, log_output=True, use_reloader=False)
