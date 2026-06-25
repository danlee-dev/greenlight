"""Update guardrail.

Before shipping an update, compare the project against the last approved version
and flag newly-risky changes (a new permission, a new SDK, a new third-party AI
endpoint, changed data collection, a lowered target SDK), so a routine update
does not silently introduce a rejection risk.

A baseline is a small, serializable snapshot of the risk-relevant facts taken
from ``audit.inspect_project``. Save one when a version is approved, then diff
the project against it before the next submission.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from . import audit

RESTRICTED_ANDROID = {
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.READ_SMS", "android.permission.SEND_SMS",
    "android.permission.READ_CALL_LOG", "android.permission.MANAGE_EXTERNAL_STORAGE",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.QUERY_ALL_PACKAGES", "android.permission.SCHEDULE_EXACT_ALARM",
}
SNAPSHOT_VERSION = 1


def snapshot(project_path: str, platform: str = "both") -> dict[str, Any]:
    facts = audit.inspect_project(project_path)
    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "platform": platform,
        "platforms_detected": sorted(facts.platforms),
        "app_name": facts.app_name,
        "bundle_id": facts.bundle_id,
        "package": facts.package,
        "ios_usage_keys": sorted(facts.ios_usage.keys()),
        "sensitive_frameworks": sorted(facts.sensitive_frameworks),
        "android_permissions": sorted(facts.android_permissions),
        "target_sdk": facts.target_sdk,
        "ai_endpoints": sorted(facts.ai_endpoints),
        "payment_sdks": sorted(facts.payment_sdks),
        "webview": facts.webview,
        "has_privacy_manifest": facts.has_privacy_manifest,
        "privacy_policy_url": facts.privacy_policy_url,
    }


def _set_added_removed(base, cur) -> tuple[list, list]:
    base_s, cur_s = set(base or []), set(cur or [])
    return sorted(cur_s - base_s), sorted(base_s - cur_s)


def diff(baseline: dict, current: dict) -> list[dict]:
    changes: list[dict] = []

    def add(field, kind, risk, detail):
        changes.append({"field": field, "kind": kind, "risk": risk, "detail": detail})

    added, removed = _set_added_removed(baseline.get("android_permissions"),
                                        current.get("android_permissions"))
    for p in added:
        add("android_permissions", "added",
            "high" if p in RESTRICTED_ANDROID else "med", f"New permission: {p}")
    for p in removed:
        add("android_permissions", "removed", "low", f"Removed permission: {p}")

    added, removed = _set_added_removed(baseline.get("ai_endpoints"), current.get("ai_endpoints"))
    for a in added:
        add("ai_endpoints", "added", "high",
            f"New third-party AI signal: {a} -- requires 5.1.2(i) disclosure + consent.")
    for a in removed:
        add("ai_endpoints", "removed", "low", f"Removed AI signal: {a}")

    added, removed = _set_added_removed(baseline.get("payment_sdks"), current.get("payment_sdks"))
    for s in added:
        add("payment_sdks", "added", "med", f"New payment SDK: {s} -- check IAP requirement (3.1.1).")

    added, removed = _set_added_removed(baseline.get("sensitive_frameworks"),
                                        current.get("sensitive_frameworks"))
    for fw in added:
        add("sensitive_frameworks", "added", "med", f"New sensitive data access: {fw}.")

    added, removed = _set_added_removed(baseline.get("ios_usage_keys"), current.get("ios_usage_keys"))
    for k in removed:
        add("ios_usage_keys", "removed", "med", f"Removed purpose string: {k}.")

    base_sdk, cur_sdk = baseline.get("target_sdk"), current.get("target_sdk")
    if base_sdk != cur_sdk:
        if isinstance(base_sdk, int) and isinstance(cur_sdk, int) and cur_sdk < base_sdk:
            add("target_sdk", "changed", "high", f"targetSdk lowered {base_sdk} -> {cur_sdk}.")
        else:
            add("target_sdk", "changed", "low", f"targetSdk {base_sdk} -> {cur_sdk}.")

    if baseline.get("has_privacy_manifest") and not current.get("has_privacy_manifest"):
        add("has_privacy_manifest", "removed", "high", "PrivacyInfo.xcprivacy was removed.")
    if baseline.get("privacy_policy_url") and not current.get("privacy_policy_url"):
        add("privacy_policy_url", "removed", "high", "Privacy policy URL was removed.")
    if current.get("webview") and not baseline.get("webview"):
        add("webview", "added", "med", "WebView newly introduced -- watch 4.2 wrapper risk.")

    b_bundle, c_bundle = baseline.get("bundle_id"), current.get("bundle_id")
    if b_bundle and c_bundle and b_bundle != c_bundle:
        add("bundle_id", "changed", "high", f"Bundle id changed {b_bundle} -> {c_bundle}.")

    return changes


def guard(project_path: str, platform: str = "both",
          baseline: Optional[dict] = None) -> dict[str, Any]:
    current = snapshot(project_path, platform)
    if not baseline:
        return {
            "baseline_present": False,
            "snapshot": current,
            "note": "No baseline supplied. Save this snapshot when the current version is "
                    "approved, then diff future updates against it.",
        }
    changes = diff(baseline, current)
    high = sum(1 for c in changes if c["risk"] == "high")
    risky = sum(1 for c in changes if c["risk"] in ("high", "med"))
    return {
        "baseline_present": True,
        "changes": changes,
        "risky_count": risky,
        "high_risk_count": high,
        "verdict": "review-update" if risky else "clear",
    }


def save_baseline(project_path: str, platform: str = "both", out_path=None) -> Path:
    snap = snapshot(project_path, platform)
    out = Path(out_path) if out_path else Path(project_path) / ".greenlight" / "baseline.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def load_baseline(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
