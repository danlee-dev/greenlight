"""Greenlight local cockpit (scaffold).

A tiny Flask app that serves the static cockpit and a few JSON endpoints the
UI calls. The production cockpit (see BUILD_PROMPT.md) should hot-reload and
share screenshot templates with the renderer. Keep it local-only.
"""
from __future__ import annotations
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

from .. import audit as audit_mod
from .. import screenshots as shots

STATIC = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC))


@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.get("/api/specs")
def specs():
    return jsonify(shots.SPECS)


@app.get("/api/audit")
def audit():
    project = request.args.get("project", ".")
    platform = request.args.get("platform", "both")
    return jsonify(audit_mod.run(project, platform))


def serve(host: str = "127.0.0.1", port: int = 4317) -> None:
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    serve()
