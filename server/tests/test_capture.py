"""Real-screen capture: simctl parsing, error paths, and compositing a captured
screen into the renderer. Device-dependent calls are exercised via their parse
and error paths so the suite runs without a booted device."""
import json

import pytest
from PIL import Image

from greenlight_mcp import capture as cap
from greenlight_mcp import screenshots as shots

SIMCTL_SAMPLE = json.dumps({
    "devices": {
        "com.apple.CoreSimulator.SimRuntime.iOS-26-1": [
            {"udid": "AAA", "name": "iPhone 16e", "state": "Booted", "isAvailable": True},
            {"udid": "BBB", "name": "iPhone 17 Pro", "state": "Shutdown", "isAvailable": True},
            {"udid": "CCC", "name": "Unavailable", "state": "Shutdown", "isAvailable": False},
        ]
    }
})


def test_parse_ios_simulators_filters_and_flattens():
    sims = cap.parse_ios_simulators(SIMCTL_SAMPLE)
    assert {s["name"] for s in sims} == {"iPhone 16e", "iPhone 17 Pro"}  # unavailable dropped
    booted = [s for s in sims if s["state"] == "Booted"]
    assert booted and booted[0]["udid"] == "AAA"
    assert all(s["runtime"] == "iOS-26-1" for s in sims)


def test_parse_ios_simulators_bad_json():
    assert cap.parse_ios_simulators("not json") == []


def test_capture_screen_unknown_platform(tmp_path):
    with pytest.raises(cap.CaptureError):
        cap.capture_screen("windows", tmp_path / "x.png")


def test_accept_user_capture_roundtrips(tmp_path):
    src = tmp_path / "src.png"
    Image.new("RGB", (100, 200), (10, 20, 30)).save(src)
    out = cap.accept_user_capture(src, tmp_path / "out.png")
    assert out.exists() and Image.open(out).size == (100, 200)


def test_accept_user_capture_missing(tmp_path):
    with pytest.raises(cap.CaptureError):
        cap.accept_user_capture(tmp_path / "nope.png", tmp_path / "o.png")


def test_capture_android_no_device(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "_which", lambda t: "/usr/bin/adb")
    monkeypatch.setattr(cap, "list_android_devices", lambda: [])
    with pytest.raises(cap.CaptureError):
        cap.capture_android(tmp_path / "a.png")


def test_missing_tool_raises(monkeypatch):
    monkeypatch.setattr(cap.shutil, "which", lambda t: None)
    with pytest.raises(cap.CaptureError):
        cap.list_ios_simulators()


def test_render_with_real_screen_image(tmp_path):
    screen = tmp_path / "screen.png"
    Image.new("RGB", (1179, 2556), (5, 100, 80)).save(screen)
    out = shots.render_marketing_panel("iphone_6_9", "Real screen", "from a capture",
                                       tmp_path / "shot.png", screen_img=str(screen))
    assert Image.open(out).size == (1320, 2868)
