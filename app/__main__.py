from __future__ import annotations

import os

from . import create_app

app = create_app()

if __name__ == "__main__":
    exclude_patterns = [os.path.join(os.getcwd(), "sandbox", "*")]
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8008,
        exclude_patterns=exclude_patterns,
    )
