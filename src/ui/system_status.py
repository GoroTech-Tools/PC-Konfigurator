from __future__ import annotations

import threading

from ui.theme import get_status_color


def start_system_requirements_check(root, system_checker, logger, on_result) -> None:
    """Startet die Systemprüfung asynchron und liefert Ergebnis per Callback."""

    def check():
        try:
            result = system_checker.check_all_requirements()
            root.after(0, lambda: on_result(result))
        except Exception as exc:
            logger.error(f"Fehler bei Systemprüfung: {exc}")
            root.after(0, lambda: on_result({"success": False, "error": str(exc)}))

    thread = threading.Thread(target=check, daemon=True)
    thread.start()


def apply_system_status(result: dict, status_label, start_status_label=None) -> None:
    """Schreibt den Systemstatus in die vorgesehenen UI-Labels."""
    if result.get("success"):
        office_bitness = result.get("office", {}).get("bitness", "?")
        status_text = (
            f"[OK] System OK\n"
            f"Windows: {result.get('windows_version', '?')}\n"
            f"Office: {result.get('office_version', '?')} ({office_bitness})"
        )
        status_label.configure(text=status_text, text_color=get_status_color("success"), justify="left")
        if start_status_label is not None:
            start_status_label.configure(
                text=f"Status: System geprüft\n{status_text}",
                text_color=get_status_color("success"),
                justify="left",
            )
        return

    error_text = f"[FEHLER] {result.get('error', 'Unbekannter Fehler')}"
    status_label.configure(text=error_text, text_color=get_status_color("error"), justify="left")
    if start_status_label is not None:
        start_status_label.configure(
            text=f"Status: Systemprüfung fehlgeschlagen\n{error_text}",
            text_color=get_status_color("error"),
            justify="left",
        )
