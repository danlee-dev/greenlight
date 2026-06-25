"""Pre-submission audit (scaffold).

run() should: read the project, map findings to guideline sections, and return
a structured checklist. For now it returns a representative sample so the
cockpit and the MCP tool have a stable shape to build against.
See BUILD_PROMPT.md for the full rule set to implement.
"""
from __future__ import annotations
from typing import Any


def run(project_path: str, platform: str = "both") -> dict[str, Any]:
    checks = [
        {"id": "apple-2.3.3", "rule": "Apple 2.3.3 Accurate metadata",
         "status": "pass", "detail": "Screenshots match real app screens."},
        {"id": "apple-5.1.1", "rule": "Apple 5.1.1 Data collection & storage",
         "status": "warn", "detail": "Privacy policy URL not found; required if any data is collected."},
        {"id": "apple-4.3b", "rule": "Apple 4.3(b) Low-value / duplicate apps",
         "status": "warn", "detail": "App may read as a thin wrapper; add native value."},
        {"id": "google-closed-testing", "rule": "Google Play closed testing",
         "status": "fail", "detail": "New personal account needs 12 testers for 14 consecutive days."},
        {"id": "google-data-safety", "rule": "Google Play Data Safety",
         "status": "warn", "detail": "Data Safety form not completed."},
    ]
    score = round(100 * sum(1 for c in checks if c["status"] == "pass") / max(1, len(checks)))
    return {"project": project_path, "platform": platform,
            "pass_probability": score, "checks": checks}
