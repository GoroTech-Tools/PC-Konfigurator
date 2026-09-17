"""Retry-Hilfsfunktion für Dateisystem-Operationen auf aktiv synchronisierten Ordnern (OneDrive u. ä.)."""

from __future__ import annotations

import time
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
