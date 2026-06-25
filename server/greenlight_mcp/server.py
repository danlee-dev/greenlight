"""Greenlight MCP server.

Exposes review-audit, screenshot rendering, and cockpit tools to Claude Code.
This is a scaffold: audit_metadata and the cockpit are stubs to be expanded
per BUILD_PROMPT.md. generate_screenshots wraps the working Pillow engine.
"""
from __future__ import annotations
import json
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - allows import without deps installed
    FastMCP = None

from . import screenshots as shots
from . import audit as audit_mod
from . import capture as cap

ROOT = Path(__file__).resolve().parents[2]
RENDERS = ROOT / "renders"

if FastMCP is not None:
    mcp = FastMCP("greenlight")

    @mcp.tool()
    def list_specs() -> str:
        """Return the supported store asset spec sizes (2026)."""
        return json.dumps(shots.SPECS, ensure_ascii=False, indent=2)

    @mcp.tool()
    def generate_screenshots(spec: str, headline: str, subtitle: str = "",
                             locale: str = "en", screen_image: str = "") -> str:
        """Render one marketing screenshot PNG at the given spec size.

        spec: one of the keys in list_specs (e.g. 'iphone_6_9').
        screen_image: optional path to a real app-screen capture (see
        capture_app_screen) to composite into the device frame.
        Returns the output file path.
        """
        out = RENDERS / f"greenlight_{spec}_{locale}.png"
        path = shots.render_marketing_panel(spec, headline, subtitle, out,
                                            screen_img=screen_image or None)
        return str(path)

    @mcp.tool()
    def list_capture_devices() -> str:
        """List available iOS simulators and Android devices for screen capture."""
        result: dict = {}
        try:
            result["ios"] = cap.list_ios_simulators()
        except cap.CaptureError as exc:
            result["ios_error"] = str(exc)
        try:
            result["android"] = cap.list_android_devices()
        except cap.CaptureError as exc:
            result["android_error"] = str(exc)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    def capture_app_screen(platform: str, name: str = "screen", device: str = "") -> str:
        """Capture a real app screen from a booted iOS simulator or Android device.

        platform: 'ios' or 'android'. Saves a PNG under renders/ and returns its
        path, which you can pass to generate_screenshots as screen_image.
        Never fabricates UI (Apple 2.3.3).
        """
        out = RENDERS / f"capture_{platform}_{name}.png"
        try:
            path = cap.capture_screen(platform, out, device or None)
        except cap.CaptureError as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)
        return str(path)

    @mcp.tool()
    def audit_metadata(project_path: str, platform: str = "both") -> str:
        """Run a pre-submission guideline audit. Returns a JSON checklist.

        Scaffold: returns a sample structure. Expand per BUILD_PROMPT.md.
        """
        return json.dumps(audit_mod.run(project_path, platform),
                          ensure_ascii=False, indent=2)


def main() -> None:
    if FastMCP is None:
        raise SystemExit("Install dependencies first: pip install -r requirements.txt")
    mcp.run()


if __name__ == "__main__":
    main()
