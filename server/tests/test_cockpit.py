"""Cockpit serves the real audit for a given project and exposes the rich
fields the board binds (verdict/fix/manual)."""
from pathlib import Path

from greenlight_mcp.cockpit.app import app

FIX = Path(__file__).parent / "fixtures"


def test_api_audit_honors_project_query():
    c = app.test_client()
    data = c.get(f"/api/audit?project={FIX / 'ios_app'}&platform=ios").get_json()
    assert data["verdict"] == "no-go"
    assert data["checks"]
    # the fields the cockpit JS binds must all be present
    assert all(k in data["checks"][0] for k in ("rule", "status", "detail", "fix", "manual"))


def test_api_specs_ok():
    assert app.test_client().get("/api/specs").status_code == 200


def test_index_served():
    r = app.test_client().get("/")
    assert r.status_code == 200 and b"Greenlight" in r.data
