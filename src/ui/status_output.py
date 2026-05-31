from __future__ import annotations

from datetime import datetime


def append_status_text(*, text: str, target_widget=None, logger=None) -> None:
    """Schreibt eine Zeitstempel-Statuszeile in ein Text-Widget oder ins Log."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if target_widget is None:
        if logger is not None:
            logger.info(f"[{timestamp}] {text}")
        return

    target_widget.insert("end", f"[{timestamp}] {text}\n")
    target_widget.see("end")
