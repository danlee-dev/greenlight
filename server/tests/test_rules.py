"""The rule set must be well-formed and every detect.kind must be implemented."""
from greenlight_mcp import audit

REQUIRED = {"id", "store", "section", "title", "severity", "check", "fix", "detect"}


def test_rules_load():
    rules = audit.load_rules()
    assert len(rules) >= 15


def test_rule_shape_and_uniqueness():
    rules = audit.load_rules()
    ids = set()
    for r in rules:
        assert REQUIRED <= set(r), f"{r.get('id')} missing keys"
        assert r["store"] in ("apple", "google"), r["id"]
        assert r["severity"] in ("block", "warn", "info"), r["id"]
        assert r["id"] not in ids, f"duplicate id {r['id']}"
        ids.add(r["id"])


def test_every_detect_kind_is_implemented():
    for r in audit.load_rules():
        kind = r["detect"]["kind"]
        assert kind in audit.DETECTORS, f"{r['id']} uses unimplemented kind '{kind}'"
