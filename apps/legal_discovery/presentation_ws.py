from flask_socketio import join_room, emit

from .extensions import socketio


@socketio.on('join', namespace='/present')
def join(data):
    """Join a presentation room."""
    doc_id = data.get('doc_id')
    if doc_id:
        join_room(doc_id)


@socketio.on('command', namespace='/present')
def command(data):
    """Broadcast presentation commands to viewers."""
    doc_id = data.get('doc_id')
    if doc_id:
        emit('command', data, room=doc_id)
