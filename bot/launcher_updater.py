"""Safe, opt-in-capable source updater for the official PoE Build Notifier repository.

Downloads a pinned GitHub commit archive, extracts an explicit allowlist only,
backs up replaced code and rolls back file changes if installation fails.
User configuration, database files and backups are never touched.
"""
from __future__ import annotations
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPOSITORY = "Bollek231/poe-build-notifier-site"
API = "https://api.github.com/repos/" + REPOSITORY
VERSION_PATTERN = re.compile(r"^([0-9]+(?:\.[0-9]+)*)([a-z]*)$", re.I)
FILES = (
    "main.py", "storage.py", "features.py", "enhancements.py", "services.py",
    "backups.py", "game_modes.py", "runtime_settings.py", "localization.py",
    "community.py", "translation_providers.py", "launcher.pyw",
    "launcher_updater.py", "Start_PoE_Bot.bat", "Start_PoE_Bot.vbs",
    "requirements.txt", ".env.example", "VERSION",
)
MAX_DOWNLOAD = 8 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024


def version_key(version: str):
    match = VERSION_PATTERN.fullmatch(version.strip())
    if not match:
        raise ValueError("Invalid version: " + version[:50])
    return tuple(int(x) for x in match.group(1).split(".")), match.group(2).lower()


def is_newer(remote: str, local: str) -> bool:
    a, b = version_key(remote), version_key(local)
    width = max(len(a[0]), len(b[0]))
    left, right = a[0] + (0,) * (width - len(a[0])), b[0] + (0,) * (width - len(b[0]))
    if left != right:
        return left > right
    return a[1] > b[1]


def request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "PoE-Build-Notifier-Updater", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=18) as response:
        data = response.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise ValueError("Download exceeds size limit")
    return data


def current_version(folder: Path) -> str:
    return (folder / "VERSION").read_text(encoding="utf-8").strip()


def remote_release() -> tuple[str, str]:
    # The requested commit SHA is immutable; the ZIP is fetched from that same ref.
    import json
    branch = json.loads(request(API + "/commits/main"))
    sha = branch["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Invalid commit SHA")
    raw = "https://raw.githubusercontent.com/" + REPOSITORY + "/" + sha + "/bot/VERSION"
    version = request(raw).decode("utf-8").strip()
    version_key(version)
    return version, sha


def install(folder: Path, sha: str, version: str, logger=lambda _: None) -> bool:
    """Return true on successful update; false if already installed."""
    if not is_newer(version, current_version(folder)):
        return False
    archive_url = "https://codeload.github.com/" + REPOSITORY + "/zip/" + sha
    payload = request(archive_url)
    prefix = "poe-build-notifier-site-" + sha + "/bot/"
    with tempfile.TemporaryDirectory(prefix="poe-update-") as scratch:
        temp = Path(scratch)
        stage, backup = temp / "stage", temp / "backup"
        stage.mkdir()
        backup.mkdir()
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = set(archive.namelist())
            for filename in FILES:
                member_name = prefix + filename
                if member_name not in names:
                    raise ValueError("Release is missing " + filename)
                member = archive.getinfo(member_name)
                if member.is_dir() or member.file_size > MAX_FILE:
                    raise ValueError("Invalid archive member: " + filename)
                data = archive.read(member)
                if len(data) != member.file_size:
                    raise ValueError("Corrupt archive member: " + filename)
                (stage / filename).write_bytes(data)
        if (stage / "VERSION").read_text(encoding="utf-8").strip() != version:
            raise ValueError("Release version mismatch")
        changed = []
        existed = {}
        try:
            for filename in FILES:
                dest = folder / filename
                # Refuse symlink targets: never write outside installation directory.
                if dest.is_symlink():
                    raise ValueError("Refusing symlink: " + filename)
                existed[filename] = dest.exists()
                if dest.exists():
                    shutil.copy2(dest, backup / filename)
                # Apply VERSION last so an interrupted update can be retried.
                if filename == "VERSION":
                    continue
                staged = folder / (filename + ".updating")
                shutil.copy2(stage / filename, staged)
                os.replace(staged, dest)
                changed.append(filename)
            logger("Aktualizuję zależności Pythona / Updating Python dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(folder / "requirements.txt")],
                           cwd=folder, check=True, timeout=240,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            shutil.copy2(stage / "VERSION", folder / "VERSION.updating")
            os.replace(folder / "VERSION.updating", folder / "VERSION")
            changed.append("VERSION")
        except Exception:
            for filename in reversed(changed):
                dest = folder / filename
                if existed[filename]:
                    shutil.copy2(backup / filename, dest)
                else:
                    dest.unlink(missing_ok=True)
            raise
        finally:
            for filename in FILES:
                (folder / (filename + ".updating")).unlink(missing_ok=True)
    return True
