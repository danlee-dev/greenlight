"""Rejection resolver: section extraction, keyword mapping, platform filter, and
the honest no-match path."""
from greenlight_mcp import resolver


def _ids(result):
    return {m["id"] for m in result["matched"]}


def test_apple_section_citation_maps_to_rule():
    text = "Guideline 2.3.3 - Performance. Your screenshots show only the login screen."
    out = resolver.resolve(text, "ios")
    assert "2.3.3" in out["cited_sections"]
    assert "apple-2.3.3-screenshots-real" in _ids(out)


def test_third_party_ai_section_and_keyword():
    out = resolver.resolve("Guideline 5.1.2(i): you share data with a third-party AI.", "ios")
    assert "apple-5.1.2i-third-party-ai" in _ids(out)


def test_google_keyword_without_number():
    out = resolver.resolve("Your app was rejected: complete closed testing with 12 testers.", "android")
    assert "google-closed-testing" in _ids(out)


def test_app_name_length():
    out = resolver.resolve("Guideline 2.3.7 - your app name exceeds the limit.", "ios")
    assert "apple-2.3.7-name-length" in _ids(out)
    assert all(m["fix"] for m in out["matched"])


def test_platform_filter_excludes_other_store():
    # a google-only keyword under ios must not surface a google rule
    out = resolver.resolve("closed testing required", "ios")
    assert "google-closed-testing" not in _ids(out)
    assert out.get("note")  # nothing matched -> note


def test_no_match_returns_note():
    out = resolver.resolve("Some vague feedback with no guideline reference at all.", "both")
    assert out["matched"] == []
    assert "note" in out
