"""Greenlight local cockpit (scaffold).

A tiny Flask app that serves the static cockpit and a few JSON endpoints the
UI calls. The production cockpit (see BUILD_PROMPT.md) should hot-reload and
share screenshot templates with the renderer. Keep it local-only.
"""
from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

from .. import audit as audit_mod
from .. import screenshots as shots

STATIC = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC))

# The project the cockpit audits. Set via env at launch so the board can target
# the user's app, not the cockpit's own working directory; a ?project= query
# overrides per request.
DEFAULT_PROJECT = os.environ.get("GREENLIGHT_PROJECT", ".")
DEFAULT_PLATFORM = os.environ.get("GREENLIGHT_PLATFORM", "both")
DEFAULT_PORT = int(os.environ.get("GREENLIGHT_PORT", "4317"))


@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.get("/api/specs")
def specs():
    return jsonify(shots.SPECS)


@app.get("/api/audit")
def audit():
    project = request.args.get("project", DEFAULT_PROJECT)
    platform = request.args.get("platform", DEFAULT_PLATFORM)
    return jsonify(audit_mod.run(project, platform))


def serve(host: str = "127.0.0.1", port: int | None = None) -> None:
    app.run(host=host, port=port or DEFAULT_PORT, debug=False)


if __name__ == "__main__":
    serve()
