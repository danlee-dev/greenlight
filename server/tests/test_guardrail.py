"""Update guardrail: snapshot capture, risk-classified diff, and baseline I/O."""
from pathlib import Path

from greenlight_mcp import guardrail as guard

FIX = Path(__file__).parent / "fixtures"


def test_snapshot_captures_risk_signals():
    snap = guard.snapshot(str(FIX / "ios_app"), "ios")
    assert "Location" in snap["sensitive_frameworks"]
    assert any("openai" in a for a in snap["ai_endpoints"])
    assert snap["has_privacy_manifest"] is False


def test_diff_flags_new_ai_and_restricted_permission():
    base = {"android_permissions": ["android.permission.INTERNET"], "ai_endpoints": [], "target_sdk": 35}
    cur = {"android_permissions": ["android.permission.INTERNET", "android.permission.READ_SMS"],
           "ai_endpoints": ["openai"], "target_sdk": 35}
    highs = {c["field"] for c in guard.diff(base, cur) if c["risk"] == "high"}
    assert "ai_endpoints" in highs
    assert "android_permissions" in highs   # READ_SMS is restricted -> high


def test_diff_lowered_target_sdk_is_high():
    changes = guard.diff({"target_sdk": 35}, {"target_sdk": 33})
    assert any(c["field"] == "target_sdk" and c["risk"] == "high" for c in changes)


def test_diff_raised_target_sdk_is_low():
    tgt = [c for c in guard.diff({"target_sdk": 34}, {"target_sdk": 35}) if c["field"] == "target_sdk"]
    assert tgt and tgt[0]["risk"] == "low"


def test_guard_no_baseline_returns_snapshot():
    out = guard.guard(str(FIX / "ios_app"), "ios", None)
    assert out["baseline_present"] is False and "snapshot" in out


def test_guard_clear_when_identical():
    snap = guard.snapshot(str(FIX / "ios_app"), "ios")
    out = guard.guard(str(FIX / "ios_app"), "ios", snap)
    assert out["verdict"] == "clear" and out["risky_count"] == 0


def test_save_and_load_baseline_roundtrip(tmp_path):
    p = guard.save_baseline(str(FIX / "android_app"), "android", tmp_path / "b.json")
    assert p.exists()
    loaded = guard.load_baseline(p)
    assert loaded["snapshot_version"] == guard.SNAPSHOT_VERSION
    assert "android.permission.ACCESS_BACKGROUND_LOCATION" in loaded["android_permissions"]
