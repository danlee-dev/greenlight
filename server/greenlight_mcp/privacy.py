"""Privacy generator.

From a static project scan (reusing ``audit.inspect_project``), drafts:
- an Apple ``PrivacyInfo.xcprivacy`` manifest,
- Apple privacy nutrition-label answers,
- Google Data safety answers,
and flags any data access with no user-facing purpose.

Honesty: the output is a DRAFT to verify, not an authoritative declaration. A
static scan sees SDKs / permissions / endpoints but not intent, so every section
carries a note and the engine never silently claims completeness (Required
Reason APIs, for example, must be added by the developer).
"""
from __future__ import annotations

import plistlib
from typing import Any

from . import audit

# detected sensitive framework -> Apple privacy data-type constant
APPLE_DATA_TYPES = {
    "Location": "NSPrivacyCollectedDataTypePreciseLocation",
    "Photos": "NSPrivacyCollectedDataTypePhotosorVideos",
    "Contacts": "NSPrivacyCollectedDataTypeContacts",
}
# Android permission -> Google Data safety data type label
GOOGLE_DATA_TYPES = {
    "android.permission.ACCESS_FINE_LOCATION": "Precise location",
    "android.permission.ACCESS_COARSE_LOCATION": "Approximate location",
    "android.permission.ACCESS_BACKGROUND_LOCATION": "Location (background)",
    "android.permission.CAMERA": "Photos and videos",
    "android.permission.READ_CONTACTS": "Contacts",
    "android.permission.RECORD_AUDIO": "Audio",
    "android.permission.READ_SMS": "SMS messages",
    "android.permission.READ_CALL_LOG": "Call logs",
}


def _apple_manifest(facts) -> str:
    collected = []
    for label in sorted(facts.sensitive_frameworks):
        dt = APPLE_DATA_TYPES.get(label.split("/")[0])
        if dt:
            collected.append({
                "NSPrivacyCollectedDataType": dt,
                "NSPrivacyCollectedDataTypeLinked": True,
                "NSPrivacyCollectedDataTypeTracking": False,
                "NSPrivacyCollectedDataTypePurposes": [
                    "NSPrivacyCollectedDataTypePurposeAppFunctionality"],
            })
    manifest = {
        "NSPrivacyTracking": False,
        "NSPrivacyTrackingDomains": [],
        "NSPrivacyCollectedDataTypes": collected,
        # Required Reason APIs cannot be inferred from this scan; the developer
        # must declare them. Left empty intentionally (see the section note).
        "NSPrivacyAccessedAPITypes": [],
    }
    return plistlib.dumps(manifest).decode("utf-8")


def _apple_label(facts) -> list[dict]:
    items: list[dict] = []
    for label in sorted(facts.sensitive_frameworks):
        items.append({
            "data_type": label,
            "collected": True,
            "linked_to_user": "confirm",
            "used_for_tracking": False,
            "purpose": "App Functionality",
        })
    if facts.ai_endpoints:
        items.append({
            "data_type": "Data sent to third-party AI",
            "providers": facts.ai_endpoints,
            "note": "Apple 5.1.2(i): name the provider and obtain explicit in-app consent.",
        })
    return items


def _google_data_safety(facts) -> dict:
    collected = []
    for perm in facts.android_permissions:
        dt = GOOGLE_DATA_TYPES.get(perm)
        if dt:
            collected.append({
                "data_type": dt,
                "collected": True,
                "shared": bool(facts.ai_endpoints),
                "purpose": "App functionality",
                "encrypted_in_transit": "confirm",
            })
    return {
        "collects_data": bool(collected) or bool(facts.ai_endpoints),
        "data_types": collected,
        "shared_with_third_parties": list(facts.ai_endpoints),
        "deletion_available": "confirm" if facts.login_detected else "n/a (no account)",
    }


def _flags(facts) -> list[str]:
    flags: list[str] = []
    declared = {k.replace("UsageDescription", "").replace("NS", "").lower()
                for k in facts.ios_usage}
    if "ios" in facts.platforms:
        for label in sorted(facts.sensitive_frameworks):
            token = label.split("/")[0].lower()
            if not any(token in d for d in declared):
                flags.append(f"{label} is accessed with no NS*UsageDescription -- "
                             "add a purpose string or remove the access.")
    if facts.ai_endpoints:
        flags.append(f"Personal data may be shared with third-party AI "
                     f"({', '.join(facts.ai_endpoints)}) -- declare it as sharing and add "
                     "an in-app disclosure + explicit consent.")
    if not facts.privacy_policy_url:
        flags.append("No privacy policy URL provided (set privacy_policy_url in "
                     "greenlight.json) -- both stores require one.")
    return flags


def generate(project_path: str, platform: str = "both") -> dict[str, Any]:
    facts = audit.inspect_project(project_path)
    stores = audit._target_stores(platform)
    out: dict[str, Any] = {
        "project": str(facts.path),
        "platform": platform,
        "platforms_detected": sorted(facts.platforms),
        "flags": _flags(facts),
    }
    if "apple" in stores:
        out["apple"] = {
            "privacy_manifest_xcprivacy": _apple_manifest(facts),
            "nutrition_label": _apple_label(facts),
            "note": "Draft from a static scan. Add Required Reason API declarations "
                    "and confirm linkage/tracking before submitting.",
        }
    if "google" in stores:
        out["google"] = {
            "data_safety": _google_data_safety(facts),
            "note": "Draft from a static scan. Reconcile with the privacy policy and "
                    "actual SDK behavior before submitting.",
        }
    return out
