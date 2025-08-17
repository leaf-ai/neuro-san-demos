from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)

__all__ = ["socketio", "limiter"]
