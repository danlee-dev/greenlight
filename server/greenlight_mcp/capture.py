"""Real-screen capture for the screenshot studio.

Captures actual app screens from a booted iOS Simulator or an Android
device/emulator -- Apple 2.3.3 requires screenshots to show the real app, so we
never fabricate UI -- or accepts a user-provided image. The capture is then
composited into a device frame by
``screenshots.render_marketing_panel(..., screen_img=...)``.

macOS first: iOS uses ``xcrun simctl``, Android uses ``adb``.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from PIL import Image


class CaptureError(RuntimeError):
    """A screen could not be captured (missing tool, no device, or bad output)."""


def _which(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        hint = ("Install the Xcode command line tools." if tool == "xcrun"
                else "Install the Android platform tools (adb).")
        raise CaptureError(f"'{tool}' not found on PATH. {hint}")
    return path


def _run(cmd: list[str], timeout: int = 60, stdout=None) -> subprocess.CompletedProcess:
    capture = stdout is None
    try:
        return subprocess.run(cmd, capture_output=capture, stdout=stdout,
                              timeout=timeout, check=True, text=capture)
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.strip() if isinstance(exc.stderr, str) else ""
        raise CaptureError(f"{cmd[0]} failed: {err or exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CaptureError(f"{cmd[0]} timed out after {timeout}s") from exc


def _validate_png(path: Path) -> Path:
    try:
        with Image.open(path) as im:
            im.verify()
    except Exception as exc:
        raise CaptureError(f"Capture did not produce a valid image: {path} ({exc})") from exc
    return path


# -------------------------------------------------------------------- iOS
def parse_ios_simulators(simctl_json: str) -> list[dict]:
    """Flatten ``xcrun simctl list devices --json`` into available simulators."""
    try:
        data = json.loads(simctl_json)
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    for runtime, devices in (data.get("devices") or {}).items():
        rt = runtime.rsplit(".", 1)[-1]   # e.g. iOS-26-1
        for d in devices:
            if not d.get("isAvailable", False):
                continue
            out.append({"udid": d.get("udid"), "name": d.get("name"),
                        "state": d.get("state"), "runtime": rt})
    return out


def list_ios_simulators() -> list[dict]:
    _which("xcrun")
    res = _run(["xcrun", "simctl", "list", "devices", "--json"])
    return parse_ios_simulators(res.stdout)


def booted_ios_simulator() -> Optional[dict]:
    for d in list_ios_simulators():
        if d.get("state") == "Booted":
            return d
    return None


def capture_ios(out_path, udid: str = "booted") -> Path:
    _which("xcrun")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if udid == "booted" and not booted_ios_simulator():
        avail = ", ".join(f"{d['name']} ({d['state']})" for d in list_ios_simulators()[:8]) or "none"
        raise CaptureError(
            "No booted iOS simulator. Boot one with `xcrun simctl boot <udid>` and open "
            f"Simulator, then retry. Available: {avail}")
    _run(["xcrun", "simctl", "io", udid, "screenshot", str(out)])
    return _validate_png(out)


# ---------------------------------------------------------------- Android
def list_android_devices() -> list[str]:
    _which("adb")
    res = _run(["adb", "devices"])
    devices = []
    for line in res.stdout.splitlines()[1:]:   # first line is the header
        parts = line.split()
        if len(parts) == 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def capture_android(out_path, serial: Optional[str] = None) -> Path:
    _which("adb")
    if not list_android_devices():
        raise CaptureError("No Android device/emulator connected. Start an emulator or "
                           "connect a device (check `adb devices`).")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["adb"] + (["-s", serial] if serial else []) + ["exec-out", "screencap", "-p"]
    with open(out, "wb") as fh:
        _run(cmd, stdout=fh)
    return _validate_png(out)


# ------------------------------------------------- user-provided + dispatch
def accept_user_capture(src, out_path) -> Path:
    src = Path(src)
    if not src.exists():
        raise CaptureError(f"Image not found: {src}")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        Image.open(src).convert("RGB").save(out, "PNG")
    except Exception as exc:
        raise CaptureError(f"Not a readable image: {src} ({exc})") from exc
    return _validate_png(out)


def capture_screen(platform: str, out_path, device: Optional[str] = None) -> Path:
    platform = (platform or "").lower()
    if platform == "ios":
        return capture_ios(out_path, device or "booted")
    if platform == "android":
        return capture_android(out_path, device)
    raise CaptureError(f"Unknown platform '{platform}' (expected 'ios' or 'android').")
