from flask import Blueprint, jsonify, request

from coded_tools.legal_discovery.chat_agent import RetrievalChatAgent
from coded_tools.legal_discovery.timeline_manager import TimelineManager

from .database import db
from .models import MessageAuditLog
from .extensions import socketio
from .chat_state import user_input_queue
from .voice import synthesize_voice
from .stt import stream_transcribe
from .voice_commands import execute_command

import base64


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _handle_transcript(transcript: str, data: dict) -> dict:
    """Common handler for processing a user transcript."""
    user_input_queue.put(transcript)
    agent = RetrievalChatAgent()
    result = agent.query(
        question=transcript,
        sender_id=data.get("sender_id", 0),
        conversation_id=data.get("conversation_id"),
    )
    if not result.get("conversation_id"):
        from .models import Message

        msg = Message.query.get(result.get("message_id"))
        if msg:
            result["conversation_id"] = msg.conversation_id
    response_text = result.get("answer") or "\n".join(result.get("facts", []))
    if response_text:
        socketio.emit("update_speech", {"data": response_text}, namespace="/chat")
        audio = synthesize_voice(response_text, data.get("voice_model", "en-US"))
        socketio.emit("voice_output", {"audio": audio}, namespace="/chat")
        db.session.add(
            MessageAuditLog(
                message_id=result["message_id"],
                sender="assistant",
                transcript=response_text,
                voice_model=data.get("voice_model"),
            )
        )
    db.session.add(
        MessageAuditLog(
            message_id=result["message_id"],
            sender="user",
            transcript=transcript,
            voice_model=data.get("voice_model"),
        )
    )
    db.session.commit()
    return {
        "status": "ok",
        "message_id": result["message_id"],
        "conversation_id": result.get("conversation_id"),
    }

@chat_bp.post("/query")
def query_agent():
    data = request.get_json() or {}
    text = data.get("text")
    if not text:
        return jsonify({"status": "error", "error": "text required"}), 400
    tm = TimelineManager()
    case_id = data.get("case_id", 1)
    if text.lower().startswith("timeline summary"):
        return jsonify({"status": "ok", "summary": tm.summarize(case_id)})
    event = tm.upsert_event_from_text(text, case_id)
    if event:
        socketio.emit(
            "update_speech",
            {"data": f"Recorded event on {event['date']}"},
            namespace="/chat",
        )
    user_input_queue.put(text)
    agent = RetrievalChatAgent()
    result = agent.query(
        question=text,
        sender_id=data.get("sender_id", 0),
        conversation_id=data.get("conversation_id"),
    )
    if not result.get("conversation_id"):
        from .models import Message

        msg = Message.query.get(result.get("message_id"))
        if msg:
            result["conversation_id"] = msg.conversation_id
    response_text = result.get("answer") or "\n".join(result.get("facts", []))
    if response_text:
        socketio.emit("update_speech", {"data": response_text}, namespace="/chat")
        db.session.add(
            MessageAuditLog(
                message_id=result["message_id"],
                sender="assistant",
                transcript=response_text,
                voice_model=data.get("voice_model"),
            )
        )
    db.session.add(
        MessageAuditLog(
            message_id=result["message_id"],
            sender="user",
            transcript=text,
            voice_model=data.get("voice_model"),
        )
    )
    db.session.commit()
    return jsonify(
        {
            "status": "ok",
            "message_id": result["message_id"],
            "conversation_id": result.get("conversation_id"),
        }
    )


@chat_bp.post("/voice")
def voice_query():
    data = request.get_json() or {}
    transcript = data.get("transcript")
    if not transcript:
        return jsonify({"status": "error", "error": "transcript required"}), 400

    command = execute_command(transcript, data)
    if command:
        keyword, output = command
        result = _handle_transcript(transcript, data)
        db.session.add(
            MessageAuditLog(
                message_id=result["message_id"],
                sender="command",
                transcript=keyword,
                voice_model=data.get("voice_model"),
            )
        )
        db.session.commit()
        return jsonify({"status": "ok", "command": keyword, "result": output, "message_id": result["message_id"]})

    result = _handle_transcript(transcript, data)
    return jsonify(result)


@socketio.on("voice_query", namespace="/chat")
def voice_query_ws(data):
    """Handle streaming audio frames over WebSocket."""
    frames = data.get("frames") or []
    if not frames:
        socketio.emit("voice_error", {"error": "no audio"}, namespace="/chat")
        return

    audio_iter = (base64.b64decode(f) for f in frames)
    final_text = ""
    for chunk in stream_transcribe(audio_iter):
        if chunk.get("error"):
            socketio.emit("voice_error", {"error": chunk["error"]}, namespace="/chat")
            return
        if chunk["is_final"]:
            final_text = chunk["text"]
        else:
            socketio.emit(
                "voice_transcript",
                {"text": chunk["text"], "final": False},
                namespace="/chat",
            )

    if not final_text:
        socketio.emit(
            "voice_error", {"error": "transcription_unavailable"}, namespace="/chat"
        )
        return

    socketio.emit(
        "voice_transcript", {"text": final_text, "final": True}, namespace="/chat"
    )
    result = _handle_transcript(final_text, data)
    return {"text": final_text, "conversation_id": result.get("conversation_id")}


__all__ = ["chat_bp"]
