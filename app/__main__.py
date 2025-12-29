from __future__ import annotations

import os

from . import create_app
from .socketio import socketio

app = create_app()

if __name__ == "__main__":
    exclude_patterns = [os.path.join(os.getcwd(), "sandbox", "*")]
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=8008,
        exclude_patterns=exclude_patterns,
        allow_unsafe_werkzeug=True,
    )
