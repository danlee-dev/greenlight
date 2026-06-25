"""Rejection resolver.

Paste an App Store or Google Play rejection message and get the root-cause
rules and concrete fixes. The engine extracts cited guideline sections (Apple
numbers like 2.3.3 / 4.3(b) / 5.1.2(i)) and known keywords from the text and
maps them to the ``rules.yaml`` rule set. Drafting the reply to App Review is
left to the command prompt; this provides the structured diagnosis.
"""
from __future__ import annotations

import re
from typing import Any

from . import audit

# section tokens like 2.1, 2.3.3, 4.3(b), 5.1.2(i)
_SECTION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?(?:\([a-z]+\)|\([ivxlc]+\))?", re.IGNORECASE)

# keyword -> rule ids, for rejections that name a problem instead of a number
# (Google does not number its policies).
KEYWORDS: dict[str, list[str]] = {
    "screenshot": ["apple-2.3.3-screenshots-real"],
    "splash": ["apple-2.3.3-screenshots-real"],
    "privacy policy": ["apple-5.1.1-privacy-policy", "google-privacy-policy"],
    "crash": ["apple-2.1-placeholders"],
    "demo account": ["apple-2.1-demo-account"],
    "demo credentials": ["apple-2.1-demo-account"],
    "placeholder": ["apple-2.1-placeholders"],
    "purpose string": ["apple-5.1.1-purpose-strings"],
    "usage description": ["apple-5.1.1-purpose-strings"],
    "background location": ["google-restricted-permissions"],
    "data safety": ["google-data-safety"],
    "closed testing": ["google-closed-testing"],
    "12 testers": ["google-closed-testing"],
    "14 days": ["google-closed-testing"],
    "target api": ["google-target-api"],
    "in-app purchase": ["apple-3.1.1-external-payment"],
    "third-party ai": ["apple-5.1.2i-third-party-ai"],
    "third party ai": ["apple-5.1.2i-third-party-ai"],
    "web view": ["apple-4.2-webview-wrapper"],
    "webview": ["apple-4.2-webview-wrapper"],
    "wrapper": ["apple-4.2-webview-wrapper"],
    "app name": ["apple-2.3.7-name-length"],
}


def _section_matches(cited: set[str], rule_section: str) -> bool:
    rs = rule_section.lower()
    for c in cited:
        c = c.lower()
        if c == rs or rs.startswith(c) or c.startswith(rs):
            return True
    return False


def resolve(rejection_text: str, platform: str = "both") -> dict[str, Any]:
    text = rejection_text or ""
    low = text.lower()
    stores = audit._target_stores(platform)
    try:
        rules = audit.load_rules()
    except Exception as exc:
        return {"error": f"Could not load rules: {exc}", "matched": []}

    cited = {m.group(0) for m in _SECTION_RE.finditer(text)}
    by_id = {r["id"]: r for r in rules if r.get("store") in stores}

    matched_ids: set[str] = set()
    for r in by_id.values():
        if _section_matches(cited, r.get("section", "")):
            matched_ids.add(r["id"])
    for kw, ids in KEYWORDS.items():
        if kw in low:
            matched_ids.update(i for i in ids if i in by_id)

    matched = [{
        "id": r["id"],
        "store": r["store"],
        "section": r["section"],
        "rule": r["title"],
        "why": r["check"],
        "fix": r["fix"],
    } for r in (by_id[i] for i in matched_ids)]
    matched.sort(key=lambda m: (m["store"], m["section"]))

    out: dict[str, Any] = {
        "platform": platform,
        "cited_sections": sorted(cited),
        "matched": matched,
        "suggested_actions": [m["fix"] for m in matched],
    }
    if not matched:
        out["note"] = ("No rule matched automatically. Read the cited section(s) on the "
                       "official guideline page and address the reviewer's specific point; "
                       "this rejection needs manual interpretation.")
    return out
