"""Audit engine: output shape, real detection on fixtures, and the core
honesty guarantee -- no false 'all clear' on a project with real problems."""
from pathlib import Path

from greenlight_mcp import audit

FIX = Path(__file__).parent / "fixtures"


def _by_id(result):
    return {c["id"]: c for c in result["checks"]}


def test_output_shape_stable():
    res = audit.run(str(FIX / "ios_app"), "ios")
    for key in ("project", "platform", "pass_probability", "verdict", "blockers", "checks"):
        assert key in res, key
    for c in res["checks"]:
        assert {"id", "rule", "status", "detail", "section", "severity", "fix", "manual"} <= set(c)
        assert c["status"] in ("pass", "warn", "fail")


def test_ios_fixture_detects_real_problems():
    res = audit.run(str(FIX / "ios_app"), "ios")
    checks = _by_id(res)
    # 30-char name limit: the fixture name is far too long
    assert checks["apple-2.3.7-name-length"]["status"] == "fail"
    # CoreLocation used with no location purpose string
    assert checks["apple-5.1.1-purpose-strings"]["status"] == "fail"
    # third-party AI endpoint present -> must be flagged
    assert checks["apple-5.1.2i-third-party-ai"]["status"] == "warn"
    # no privacy manifest in the fixture
    assert checks["apple-privacy-manifest"]["status"] == "warn"


def test_ios_fixture_is_not_all_clear():
    res = audit.run(str(FIX / "ios_app"), "ios")
    assert res["verdict"] == "no-go"
    assert res["blockers"] >= 1
    assert res["pass_probability"] < 100


def test_android_fixture_target_sdk_and_permissions():
    res = audit.run(str(FIX / "android_app"), "android")
    checks = _by_id(res)
    assert checks["google-target-api"]["status"] == "fail"      # targetSdk 33 < 35
    assert checks["google-restricted-permissions"]["status"] == "warn"  # background location
    assert res["verdict"] == "no-go"


def test_platform_filter_excludes_other_store():
    # an iOS project audited as android should not invent apple checks
    res = audit.run(str(FIX / "ios_app"), "android")
    assert all(c["id"].startswith("google-") for c in res["checks"]) or res["checks"] == []


def test_missing_project_does_not_crash():
    res = audit.run(str(FIX / "does_not_exist"), "both")
    assert res["pass_probability"] >= 0
    assert isinstance(res["checks"], list)


# --- regression guards for the adversarial-review fixes --------------------

def test_clean_ios_can_be_go():
    res = audit.run(str(FIX / "ios_clean"), "ios")
    assert res["verdict"] == "go"
    assert res["pass_probability"] >= 90
    assert res["blockers"] == 0 and res["unconfirmed_blockers"] == 0


def test_unverified_block_is_never_go():
    # An android project with only a manifest: targetSdk / privacy policy /
    # closed testing are all unverifiable hard requirements -> must not be "go".
    res = audit.run(str(FIX / "android_minimal"), "android")
    assert res["verdict"] != "go"
    assert res["unconfirmed_blockers"] >= 1
    assert res["pass_probability"] < 100
    tgt = _by_id(res)["google-target-api"]
    assert tgt["status"] == "warn" and tgt["manual"]


def test_guaranteed_reject_scores_low():
    # The long-name iOS fixture is a guaranteed reject; the score must reflect it.
    res = audit.run(str(FIX / "ios_app"), "ios")
    assert res["verdict"] == "no-go"
    assert res["pass_probability"] <= 30


def test_target_sdk_multi_digit(tmp_path):
    (tmp_path / "AndroidManifest.xml").write_text(
        '<manifest package="x"><application/></manifest>', encoding="utf-8")
    (tmp_path / "build.gradle").write_text(
        "defaultConfig { targetSdkVersion 100 }", encoding="utf-8")
    facts = audit.inspect_project(str(tmp_path))
    assert facts.target_sdk == 100


def test_payment_word_boundary(tmp_path):
    (tmp_path / "Info.plist").write_text(
        '<?xml version="1.0"?><plist version="1.0"><dict>'
        '<key>CFBundleName</key><string>X</string></dict></plist>', encoding="utf-8")
    # "stripeColor" / "...paypalless" must NOT trip the payment detector
    (tmp_path / "Theme.swift").write_text("let stripeColor = 1\nlet hairlinePaypalless = 2\n", encoding="utf-8")
    assert _by_id(audit.run(str(tmp_path), "ios"))["apple-3.1.1-external-payment"]["status"] == "pass"
    # a real import must trip it
    (tmp_path / "Pay.swift").write_text("import Stripe\n", encoding="utf-8")
    assert _by_id(audit.run(str(tmp_path), "ios"))["apple-3.1.1-external-payment"]["status"] == "warn"


def test_metadata_word_boundary(tmp_path):
    (tmp_path / "Info.plist").write_text(
        '<?xml version="1.0"?><plist version="1.0"><dict>'
        '<key>CFBundleName</key><string>Garden</string></dict></plist>', encoding="utf-8")
    # "windowsill" must NOT match the "windows" forbidden token
    (tmp_path / "greenlight.json").write_text(
        '{"app_name":"Garden","description":"a cozy windowsill garden planner"}', encoding="utf-8")
    assert _by_id(audit.run(str(tmp_path), "ios"))["apple-2.3.10-other-platforms"]["status"] == "pass"
