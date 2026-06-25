"""Pre-submission audit engine.

run() inspects a real project, evaluates it against the rule set in
skills/app-review-guidelines/rules.yaml, and returns a structured checklist
with a go/no-go verdict and a pass-probability score.

Design notes:
- The output shape is stable so the cockpit and MCP tool keep working:
  {project, platform, pass_probability, verdict, blockers, checks[]}
  and each check keeps {id, rule, status, detail} plus section/severity/fix/manual.
- Honesty rule (BUILD_PROMPT section 8.1): never emit a false "all clear".
    - Anything that cannot be verified statically (login-gated console state,
      human judgement) is surfaced as a manual-check warning, never a silent pass.
    - A "go" verdict requires every block-severity rule to be a CONFIRMED pass.
      An unverified block requirement (manual warn) blocks "go" and caps the score.
- Detection is best-effort and static; token scans use word-boundary matching to
  avoid false positives (e.g. "stripeColor"), and a truncated scan is disclosed.
"""
from __future__ import annotations

import functools
import os
import plistlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import yaml
except Exception:  # pragma: no cover - degrade gracefully if pyyaml missing
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = ROOT / "skills" / "app-review-guidelines" / "rules.yaml"

STORE_LABEL = {"apple": "Apple", "google": "Google Play"}
STORE_PLATFORM = {"apple": "ios", "google": "android"}

# --- static-scan signal tokens (matched case-insensitively, word-bounded) ---
# AI providers: hostnames and provider/markers, so a proxy or split string still
# tends to surface at least one token. Absence is best-effort, not a guarantee.
AI_MARKERS = [
    "api.openai.com", "openai", "anthropic", "generativelanguage", "cohere.ai",
    "mistral.ai", "x.ai", "huggingface", "/v1/chat/completions", "gpt-4", "claude-3",
]
PAYMENT_SDKS = ["stripe", "braintree", "paypal", "adyen", "squareup", "razorpay"]
WEBVIEW_TOKENS = ["wkwebview", "uiwebview", "android.webkit.webview"]
RUNTIME_EXEC = ["evaluatescript", "jscontext", "dlopen", "loadstring"]
PLACEHOLDERS = ["lorem ipsum", "coming soon", "your text here", "insert text here", "placeholder text"]
LOGIN_TOKENS = ["signinwithapple", "loginviewcontroller", "isloggedin", "oauth", "authviewmodel"]
STOREKIT_TOKENS = ["import storekit", "skproduct", "skpaymentqueue", "storekit2"]
SENSITIVE_FRAMEWORKS = {
    "corelocation": "Location", "cllocationmanager": "Location",
    "avcapturedevice": "Camera", "avfoundation": "Camera/Microphone",
    "phphotolibrary": "Photos", "cncontactstore": "Contacts",
}

# directories that never hold reviewable source; skipped during the walk
SKIP_DIRS = {
    ".git", "node_modules", "build", ".build", "pods", "deriveddata", ".venv",
    "venv", "dist", ".gradle", "__pycache__", ".next", ".idea", "vendor",
}
SOURCE_EXT = {
    ".swift", ".m", ".mm", ".h", ".kt", ".java", ".js", ".ts", ".tsx", ".jsx",
    ".dart", ".json", ".plist", ".xml", ".gradle", ".kts", ".pbxproj", ".strings",
}
MAX_FILE_BYTES = 512 * 1024          # skip individual files larger than this
MAX_SOURCE_FILES = 6000              # cap how many source files we read text from
MAX_BLOB_BYTES = 40 * 1024 * 1024    # cap total scanned source text


@functools.lru_cache(maxsize=None)
def _word_re(token: str) -> re.Pattern:
    # word-ish boundary: token must not be flanked by another [a-z0-9] character,
    # so "stripe" matches "import stripe" / "api.stripe.com" but not "stripeColor".
    return re.compile(r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])")


def _has(blob: str, token: str) -> bool:
    return _word_re(token).search(blob) is not None


@dataclass
class ProjectFacts:
    path: str
    platforms: set = field(default_factory=set)
    app_name: Optional[str] = None
    bundle_id: Optional[str] = None
    package: Optional[str] = None
    ios_usage: dict = field(default_factory=dict)     # NS*UsageDescription -> value
    sensitive_frameworks: set = field(default_factory=set)
    has_privacy_manifest: bool = False
    has_storekit: bool = False
    android_permissions: list = field(default_factory=list)
    target_sdk: Optional[int] = None
    ai_endpoints: list = field(default_factory=list)
    payment_sdks: list = field(default_factory=list)
    webview: bool = False
    runtime_exec: bool = False
    placeholders: list = field(default_factory=list)
    login_detected: bool = False
    privacy_policy_url: Optional[str] = None
    metadata_text: str = ""
    scan_truncated: bool = False
    config: dict = field(default_factory=dict)


# --------------------------------------------------------------------------
# Inspection
# --------------------------------------------------------------------------
def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _load_config(root: Path) -> dict:
    """Optional greenlight.json supplies metadata the project files lack
    (app_name, privacy_policy_url, description, keywords, subtitle)."""
    for name in ("greenlight.json", ".greenlight.json"):
        p = root / name
        if p.exists():
            try:
                import json
                return json.loads(_read_text(p)) or {}
            except Exception:
                return {}
    return {}


def _parse_info_plist(path: Path, facts: ProjectFacts) -> None:
    try:
        with open(path, "rb") as fh:
            data = plistlib.load(fh)
    except Exception:
        return
    if not isinstance(data, dict):
        return
    name = data.get("CFBundleDisplayName") or data.get("CFBundleName")
    if isinstance(name, str) and name and "$(" not in name and not facts.app_name:
        facts.app_name = name
    bid = data.get("CFBundleIdentifier")
    if isinstance(bid, str) and "$(" not in bid and not facts.bundle_id:
        facts.bundle_id = bid
    for key, val in data.items():
        if key.endswith("UsageDescription"):
            facts.ios_usage[key] = val if isinstance(val, str) else ""


def _parse_android_manifest(path: Path, facts: ProjectFacts) -> None:
    text = _read_text(path)
    if not text:
        return
    try:
        root = ET.fromstring(text)
    except Exception:
        # fall back to regex if the manifest has unbound namespaces etc.
        for m in re.finditer(r'uses-permission[^>]*android:name="([^"]+)"', text):
            facts.android_permissions.append(m.group(1))
        return
    ns = "{http://schemas.android.com/apk/res/android}"
    pkg = root.get("package")
    if pkg and not facts.package:
        facts.package = pkg
    for el in root.iter("uses-permission"):
        name = el.get(ns + "name") or el.get("name")
        if name:
            facts.android_permissions.append(name)


def _parse_target_sdk(text: str, facts: ProjectFacts) -> None:
    if facts.target_sdk is not None:
        return
    m = re.search(r'targetSdk(?:Version)?\s*[=\s(]\s*["\']?(\d+)', text)
    if m:
        try:
            facts.target_sdk = int(m.group(1))
        except ValueError:
            pass


def inspect_project(project_path: str) -> ProjectFacts:
    root = Path(project_path).expanduser().resolve()
    facts = ProjectFacts(path=str(root))
    if not root.exists():
        return facts

    facts.config = _load_config(root)
    blob_parts: list[str] = []
    blob_budget = MAX_SOURCE_FILES
    blob_bytes = 0
    walk_root = root.parent if root.is_file() else root

    for dirpath, dirnames, filenames in os.walk(walk_root):
        dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
        # an .xcodeproj / .xcworkspace bundle is a directory
        if any(d.endswith((".xcodeproj", ".xcworkspace")) for d in dirnames):
            facts.platforms.add("ios")
        for fn in filenames:
            p = Path(dirpath) / fn
            low = fn.lower()

            # Structural detection is filename-based and cheap -- it ALWAYS runs,
            # so a huge asset tree can never hide the manifest/plist that decides
            # which platform-specific rules apply.
            if low == "androidmanifest.xml":
                facts.platforms.add("android")
                _parse_android_manifest(p, facts)
            elif low == "info.plist":
                facts.platforms.add("ios")
                _parse_info_plist(p, facts)
            elif low == "privacyinfo.xcprivacy":
                facts.has_privacy_manifest = True
                facts.platforms.add("ios")
            elif low in ("build.gradle", "build.gradle.kts"):
                facts.platforms.add("android")
                _parse_target_sdk(_read_text(p), facts)
            elif low == "podfile":
                facts.platforms.add("ios")

            # Source-text accumulation is the only budget-limited part.
            if p.suffix.lower() in SOURCE_EXT and blob_budget > 0 and blob_bytes < MAX_BLOB_BYTES:
                t = _read_text(p)
                if t:
                    blob_parts.append(t.lower())
                    blob_budget -= 1
                    blob_bytes += len(t)

    facts.scan_truncated = blob_budget <= 0 or blob_bytes >= MAX_BLOB_BYTES
    blob = "\n".join(blob_parts)

    facts.ai_endpoints = [m for m in AI_MARKERS if _has(blob, m)]
    facts.payment_sdks = [s for s in PAYMENT_SDKS if _has(blob, s)]
    facts.webview = any(_has(blob, t) for t in WEBVIEW_TOKENS)
    facts.runtime_exec = any(_has(blob, t) for t in RUNTIME_EXEC)
    facts.has_storekit = any(_has(blob, t) for t in STOREKIT_TOKENS)
    facts.placeholders = [p for p in PLACEHOLDERS if p in blob]   # phrases: substring is intended
    facts.login_detected = any(_has(blob, t) for t in LOGIN_TOKENS)
    facts.sensitive_frameworks = {label for tok, label in SENSITIVE_FRAMEWORKS.items() if _has(blob, tok)}

    # config overrides / supplements
    cfg = facts.config
    if cfg.get("app_name"):
        facts.app_name = cfg["app_name"]
    facts.privacy_policy_url = cfg.get("privacy_policy_url")
    facts.metadata_text = " ".join(
        str(cfg.get(k, "")) for k in ("app_name", "subtitle", "keywords", "description")
    ).lower()
    if cfg.get("platform") in ("ios", "android"):
        facts.platforms.add(cfg["platform"])
    return facts


# --------------------------------------------------------------------------
# Detectors: (facts, rule) -> (status, detail, manual) or None to skip
# --------------------------------------------------------------------------
Result = Optional[tuple[str, str, bool]]


def _manual(rule) -> Result:
    return ("warn", f"{rule['check']} Verify manually -- not statically detectable.", True)


def d_manual(facts, rule) -> Result:
    return _manual(rule)


def d_placeholders(facts, rule) -> Result:
    if facts.placeholders:
        return ("warn", f"Placeholder content found: {', '.join(facts.placeholders)}.", False)
    return ("pass", "No obvious placeholder content detected.", False)


def d_login_demo_account(facts, rule) -> Result:
    if facts.login_detected:
        return ("warn", "Login flow detected -- include a working demo account in App Review notes.", True)
    return ("pass", "No login wall detected.", False)


def d_name_length(facts, rule) -> Result:
    max_len = rule["detect"].get("max", 30)
    if not facts.app_name:
        return ("warn", "App name unknown -- provide app_name in greenlight.json to check the 30-char limit.", True)
    n = len(facts.app_name)
    if n <= max_len:
        return ("pass", f'App name "{facts.app_name}" is {n} characters.', False)
    return ("fail", f'App name "{facts.app_name}" is {n} characters (> {max_len}).', False)


def d_metadata_forbidden_tokens(facts, rule) -> Result:
    tokens = rule["detect"].get("tokens", [])
    hay = facts.metadata_text or (facts.app_name or "").lower()
    if not hay.strip():
        return ("warn", "No metadata available to scan -- provide app metadata in greenlight.json.", True)
    hit = [t for t in tokens if _has(hay, t)]
    if hit:
        return ("warn", f"Metadata mentions other-platform terms: {', '.join(hit)}.", False)
    return ("pass", "No other-platform or store references in metadata.", False)


def d_payment_sdk(facts, rule) -> Result:
    if facts.payment_sdks:
        if facts.has_storekit:
            return ("warn",
                    f"Payment SDK ({', '.join(facts.payment_sdks)}) and StoreKit both present -- "
                    "digital goods must go through StoreKit; third-party payment is only for physical goods/services.",
                    False)
        return ("warn",
                f"Third-party payment SDK detected ({', '.join(facts.payment_sdks)}) and no StoreKit -- "
                "digital goods must use StoreKit IAP.", False)
    return ("pass", "No third-party digital-payment SDK detected.", False)


def d_webview_dominant(facts, rule) -> Result:
    if facts.webview and not facts.sensitive_frameworks:
        return ("warn", "WebView detected with little native capability -- risks 4.2 'repackaged website'.", False)
    if facts.webview:
        return ("warn", "WebView detected -- ensure the app adds native value beyond a wrapper.", False)
    return ("pass", "No dominant WebView wrapper detected.", False)


def d_privacy_policy_url(facts, rule) -> Result:
    if facts.privacy_policy_url:
        return ("pass", f"Privacy policy URL configured: {facts.privacy_policy_url} "
                        "(confirm it returns 200 before submitting).", False)
    return ("warn", "No privacy policy URL provided -- set privacy_policy_url in greenlight.json; "
                    "a reachable policy is required.", True)


def d_ios_purpose_strings(facts, rule) -> Result:
    if "ios" not in facts.platforms:
        return None
    # frameworks used but with no usage string at all -> real gap
    declared = {k.replace("UsageDescription", "").replace("NS", "").lower() for k in facts.ios_usage}
    missing = []
    for label in facts.sensitive_frameworks:
        token = label.split("/")[0].lower()
        if not any(token in d for d in declared):
            missing.append(label)
    boilerplate = [k for k, v in facts.ios_usage.items()
                   if (not v) or len(v.strip()) < 15 or "$(" in v]
    if missing:
        return ("fail", f"Sensitive API used without a purpose string: {', '.join(sorted(missing))}.", False)
    if boilerplate:
        return ("warn", f"Boilerplate/empty/unsubstituted purpose strings: {', '.join(boilerplate)}.", False)
    if facts.ios_usage:
        return ("pass", f"{len(facts.ios_usage)} purpose string(s) present and specific.", False)
    return ("pass", "No sensitive permission usage strings required.", False)


def d_ios_privacy_manifest(facts, rule) -> Result:
    if "ios" not in facts.platforms:
        return None
    if facts.has_privacy_manifest:
        return ("pass", "PrivacyInfo.xcprivacy present.", False)
    return ("warn", "No PrivacyInfo.xcprivacy found -- add a privacy manifest.", False)


def d_ai_endpoint_consent(facts, rule) -> Result:
    if facts.ai_endpoints:
        return ("warn",
                f"Third-party AI signal detected ({', '.join(facts.ai_endpoints)}) -- "
                "ensure an in-app disclosure naming the provider + explicit consent (5.1.2(i)). "
                "Consent cannot be verified statically.", True)
    return ("pass", "No third-party AI signal detected (best-effort static scan).", False)


def d_runtime_code_exec(facts, rule) -> Result:
    if facts.runtime_exec:
        return ("warn", "Possible runtime code execution detected -- review against 2.5.2 self-containment.", False)
    return ("pass", "No runtime code-execution pattern detected.", False)


def d_android_restricted_permissions(facts, rule) -> Result:
    if "android" not in facts.platforms:
        return None
    restricted = set(rule["detect"].get("restricted", []))
    hit = [p for p in facts.android_permissions if p in restricted]
    if hit:
        short = [p.rsplit(".", 1)[-1] for p in hit]
        return ("warn", f"Restricted permission(s) declared: {', '.join(short)} -- each needs an eligible use case.", False)
    return ("pass", "No restricted permissions declared.", False)


def d_android_target_sdk(facts, rule) -> Result:
    if "android" not in facts.platforms:
        return None
    min_sdk = rule["detect"].get("min", 35)
    if facts.target_sdk is None:
        return ("warn", f"Could not read targetSdkVersion -- confirm it targets API {min_sdk}+.", True)
    if facts.target_sdk >= min_sdk:
        return ("pass", f"targetSdkVersion is {facts.target_sdk} (>= {min_sdk}).", False)
    return ("fail", f"targetSdkVersion is {facts.target_sdk} (< required {min_sdk}).", False)


DETECTORS: dict[str, Callable[[Any, dict], Result]] = {
    "manual": d_manual,
    "placeholders": d_placeholders,
    "login_demo_account": d_login_demo_account,
    "name_length": d_name_length,
    "metadata_forbidden_tokens": d_metadata_forbidden_tokens,
    "payment_sdk": d_payment_sdk,
    "webview_dominant": d_webview_dominant,
    "privacy_policy_url": d_privacy_policy_url,
    "ios_purpose_strings": d_ios_purpose_strings,
    "ios_privacy_manifest": d_ios_privacy_manifest,
    "ai_endpoint_consent": d_ai_endpoint_consent,
    "runtime_code_exec": d_runtime_code_exec,
    "android_restricted_permissions": d_android_restricted_permissions,
    "android_target_sdk": d_android_target_sdk,
}


# --------------------------------------------------------------------------
# Rule loading + scoring
# --------------------------------------------------------------------------
def load_rules() -> list[dict]:
    if yaml is None:
        raise RuntimeError("pyyaml is required to load the rule set")
    data = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))
    return data.get("rules", []) if isinstance(data, dict) else []


def _target_stores(platform: str) -> set:
    platform = (platform or "both").lower()
    if platform == "ios":
        return {"apple"}
    if platform == "android":
        return {"google"}
    return {"apple", "google"}


def _make_check(rule: dict, status: str, detail: str, manual: bool) -> dict:
    store = rule.get("store", "")
    return {
        "id": rule["id"],
        "rule": f"{STORE_LABEL.get(store, store)} {rule['section']} {rule['title']}",
        "status": status,
        "detail": detail,
        "section": rule["section"],
        "severity": rule.get("severity", "warn"),
        "fix": rule.get("fix", ""),
        "manual": manual,
    }


def _score(checks: list[dict], block_fail: int, block_unconfirmed: int) -> int:
    score = 100
    for c in checks:
        block = c["severity"] == "block"
        if c["status"] == "fail":
            score -= 40 if block else 8
        elif c["status"] == "warn":
            if block:
                score -= 14 if c.get("manual") else 12
            else:
                score -= 2 if c.get("manual") else 4
    score = max(0, min(100, score))
    # A guaranteed-reject app must never read as "likely to pass"; an unverified
    # hard requirement caps confidence too.
    if block_fail:
        score = min(score, 30)
    elif block_unconfirmed:
        score = min(score, 65)
    return score


def run(project_path: str, platform: str = "both") -> dict[str, Any]:
    stores = _target_stores(platform)

    try:
        rules = load_rules()
    except Exception as exc:  # degrade without crashing the MCP tool / cockpit
        return {
            "project": project_path, "platform": platform,
            "pass_probability": 0, "verdict": "unknown", "blockers": 0,
            "unconfirmed_blockers": 0,
            "checks": [_make_check(
                {"id": "rules-unavailable", "store": "", "section": "-",
                 "title": "Greenlight rule set", "severity": "warn",
                 "fix": "Reinstall the plugin / install pyyaml."},
                "warn", f"Could not load rules.yaml: {exc}", True)],
        }

    facts = inspect_project(project_path)
    checks: list[dict] = []

    for rule in rules:
        store = rule.get("store")
        if store not in stores:
            continue
        # skip a store's rules when the project clearly is not that platform
        if facts.platforms and STORE_PLATFORM.get(store) not in facts.platforms:
            continue
        detector = DETECTORS.get(rule.get("detect", {}).get("kind", "manual"), d_manual)
        result = detector(facts, rule)
        if result is None:
            continue
        status, detail, manual = result
        checks.append(_make_check(rule, status, detail, manual))

    if facts.scan_truncated:
        checks.append(_make_check(
            {"id": "greenlight-scan-truncated", "store": "", "section": "-",
             "title": "Static scan was truncated", "severity": "warn",
             "fix": "Run the audit on the app module directly."},
            "warn", "Source scan was truncated on a very large project; some code-level "
                    "signals may be missed. Re-run on the app module to be sure.", True))

    block_fail = [c for c in checks if c["severity"] == "block" and c["status"] == "fail"]
    block_unconfirmed = [c for c in checks if c["severity"] == "block" and c["status"] == "warn"]
    nonmanual_warn = [c for c in checks if c["status"] == "warn" and not c.get("manual")]
    any_fail = any(c["status"] == "fail" for c in checks)

    # "go" requires every block rule to be a CONFIRMED pass.
    if block_fail:
        verdict = "no-go"
    elif block_unconfirmed or any_fail or nonmanual_warn or facts.scan_truncated:
        verdict = "review"
    else:
        verdict = "go"

    return {
        "project": str(facts.path),
        "platform": platform,
        "platforms_detected": sorted(facts.platforms),
        "pass_probability": _score(checks, len(block_fail), len(block_unconfirmed)),
        "verdict": verdict,
        "blockers": len(block_fail),
        "unconfirmed_blockers": len(block_unconfirmed),
        "checks": checks,
    }
