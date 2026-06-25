"""Privacy generator: valid manifest, real detection from the project scan, and
honest flags for data access without a purpose."""
import plistlib
from pathlib import Path

from greenlight_mcp import privacy

FIX = Path(__file__).parent / "fixtures"


def test_apple_manifest_is_valid_plist():
    out = privacy.generate(str(FIX / "ios_app"), "ios")
    assert "apple" in out
    data = plistlib.loads(out["apple"]["privacy_manifest_xcprivacy"].encode("utf-8"))
    assert "NSPrivacyTracking" in data
    assert "NSPrivacyCollectedDataTypes" in data


def test_ios_collects_location_and_flags_missing_purpose_and_ai():
    out = privacy.generate(str(FIX / "ios_app"), "ios")
    data = plistlib.loads(out["apple"]["privacy_manifest_xcprivacy"].encode("utf-8"))
    types = [c["NSPrivacyCollectedDataType"] for c in data["NSPrivacyCollectedDataTypes"]]
    assert "NSPrivacyCollectedDataTypePreciseLocation" in types
    flags = " ".join(out["flags"]).lower()
    assert "location" in flags          # location used without a purpose string
    assert "ai" in flags                # third-party AI sharing
    assert "privacy policy" in flags    # no policy url provided


def test_android_data_safety_lists_sensitive_data():
    out = privacy.generate(str(FIX / "android_app"), "android")
    assert "google" in out
    labels = [d["data_type"] for d in out["google"]["data_safety"]["data_types"]]
    assert any("location" in label.lower() for label in labels)   # background location


def test_both_platforms_when_requested():
    out = privacy.generate(str(FIX / "ios_app"), "both")
    assert "apple" in out and "google" in out
