"""Every plugin manifest must be valid JSON."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_manifests_parse():
    for rel in (".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                ".mcp.json"):
        data = json.loads((REPO / rel).read_text(encoding="utf-8"))
        assert isinstance(data, dict), rel


def test_mcp_server_entry():
    mcp = json.loads((REPO / ".mcp.json").read_text(encoding="utf-8"))
    assert "greenlight" in mcp["mcpServers"]
    assert "${CLAUDE_PLUGIN_ROOT}" in " ".join(mcp["mcpServers"]["greenlight"]["args"])
