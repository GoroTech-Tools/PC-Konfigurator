from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def get_bundle_root() -> Path:
    """Liefert das Bundle-Root (EXE) oder Projekt-Root (Dev)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent.parent


def can_write_to(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def use_portable_runtime() -> bool:
    value = os.environ.get("PCONFIG_RUNTIME_MODE", "").strip().lower()
    return value in {"portable", "exe", "local"}


def get_runtime_root(*, app_name: str, version: str) -> Path:
    if getattr(sys, "frozen", False) and use_portable_runtime():
        exe_dir = Path(sys.executable).resolve().parent
        if can_write_to(exe_dir):
            return exe_dir

    appdata = os.environ.get("LOCALAPPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Local"
    return base / app_name / str(version)


def copy_path(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def cleanup_old_appdata_versions(*, app_name: str, current_version: str) -> None:
    """Entfernt veraltete Versionsordner des Anwenders unter %LOCALAPPDATA%."""
    appdata = os.environ.get("LOCALAPPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Local"
    app_base = base / app_name
    if not app_base.is_dir():
        return

    for entry in app_base.iterdir():
        if entry.is_dir() and entry.name != str(current_version):
            shutil.rmtree(entry, ignore_errors=True)


def prepare_runtime_bundle(
    *,
    app_name: str,
    version: str,
    runtime_folders: list[str],
    runtime_files: list[str],
) -> Path:
    bundle_root = get_bundle_root()
    cleanup_old_appdata_versions(app_name=app_name, current_version=version)
    runtime_root = get_runtime_root(app_name=app_name, version=version)
    runtime_root.mkdir(parents=True, exist_ok=True)

    marker = runtime_root / ".bundle-ready"
    critical_template = runtime_root / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Normal.dotm"
    if marker.exists() and critical_template.exists():
        return runtime_root

    for folder in runtime_folders:
        copy_path(bundle_root / folder, runtime_root / folder)

    for file_name in runtime_files:
        copy_path(bundle_root / file_name, runtime_root / file_name)

    (runtime_root / "logs").mkdir(parents=True, exist_ok=True)
    marker.write_text(version, encoding="utf-8")
    return runtime_root
