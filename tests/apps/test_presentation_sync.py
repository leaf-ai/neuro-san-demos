from flask import Flask
from apps.legal_discovery.extensions import socketio
import apps.legal_discovery.presentation_ws  # noqa: F401


def _create_app():
    app = Flask(__name__)
    socketio.init_app(app, logger=False, engineio_logger=False)
    return app


def test_command_broadcast():
    app = _create_app()
    presenter = socketio.test_client(app, namespace='/present')
    viewer = socketio.test_client(app, namespace='/present')
    presenter.emit('join', {'doc_id': 'demo.pdf', 'role': 'presenter'}, namespace='/present')
    viewer.emit('join', {'doc_id': 'demo.pdf', 'role': 'viewer'}, namespace='/present')
    presenter.emit('command', {'doc_id': 'demo.pdf', 'command': 'goto_page', 'page': 3}, namespace='/present')
    received = viewer.get_received('/present')
    assert any(r['name'] == 'command' and r['args'][0]['page'] == 3 for r in received)
