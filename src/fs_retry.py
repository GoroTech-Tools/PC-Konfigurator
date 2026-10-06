"""Retry-Hilfsfunktion für Dateisystem-Operationen auf aktiv synchronisierten Ordnern (OneDrive u. ä.)."""

from __future__ import annotations

import errno
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, TypeVar

_T = TypeVar("_T")


def retry_on_oserror(action: Callable[[], _T], *, attempts: int = 12, delay: float = 1.0) -> _T:
    """Wiederholt eine Dateisystem-Aktion bei transienten OSError.

    OneDrive kann während aktiver Synchronisierung neu angelegte Ordnerpfade kurzzeitig
    als nicht vorhanden melden (Platzhalter-/Reconciliation-Race). Standardmäßig wird bis
    zu ca. 12 Sekunden mit steigender Wartezeit erneut versucht, bevor der Fehler weitergereicht wird.
    """
    last_exc: OSError | None = None
    current_delay = delay
    for attempt in range(attempts):
        try:
            return action()
        except OSError as exc:
            last_exc = exc
            if attempt < attempts - 1:
                time.sleep(current_delay)
                current_delay = min(current_delay * 1.3, 3.0)
    assert last_exc is not None
    raise last_exc


def copy_file_with_retry(source: Path, destination: Path) -> None:
    """Kopiert eine Datei mit Wiederholungen und nativer Windows-Ausweichlösung."""
    def copy_action() -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(source, destination)
        except OSError as exc:
            if exc.errno != errno.EBADF:
                raise
            if sys.platform == "win32":
                result = subprocess.run(
                    [
                        "robocopy",
                        str(source.parent),
                        str(destination.parent),
                        source.name,
                        "/COPY:DAT",
                        "/IS",
                        "/IT",
                        "/R:2",
                        "/W:1",
                        "/NFL",
                        "/NDL",
                        "/NJH",
                        "/NJS",
                        "/NC",
                        "/NS",
                        "/NP",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if not 0 <= result.returncode < 8 or not destination.is_file():
                    detail = (result.stderr or result.stdout).strip()
                    raise OSError(
                        errno.EIO,
                        detail or f"Robocopy failed with exit code {result.returncode}",
                        str(destination),
                    )
            else:
                with source.open("rb") as source_file, destination.open("wb") as destination_file:
                    shutil.copyfileobj(source_file, destination_file)
                shutil.copystat(source, destination)

    retry_on_oserror(copy_action)
