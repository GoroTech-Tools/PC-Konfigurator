from __future__ import annotations

import subprocess
from tkinter import messagebox


def append_registry_restart_notice(status_textbox) -> None:
    """Hinweis für Anwender nach Registry-Anpassungen anzeigen."""
    notice = (
        "\nℹ️ Wichtiger Hinweis: Nach dem Anwenden der Registry-Einstellungen "
        "ist ein Neustart des Windows-Explorers oder eine Neuanmeldung am System empfohlen, "
        "damit alle Änderungen vollständig wirksam werden.\n"
    )
    status_textbox.insert("end", notice)


def restart_windows_explorer_with_prompt(office_configurator, status_textbox) -> None:
    """Startet den Windows-Explorer mit Rückfrage neu."""
    confirm = messagebox.askyesno(
        "Windows-Explorer neu starten",
        "Der Windows-Explorer wird jetzt neu gestartet.\n\n"
        "Dadurch werden Taskleiste und Desktop kurz neu geladen.\n"
        "Möchten Sie fortfahren?",
        icon="question",
    )

    if not confirm:
        return

    try:
        windows_result = office_configurator.configure_windows_settings()
        if not windows_result.get("success", False):
            status_textbox.insert(
                "end",
                f"⚠️ Windows-Einstellungen konnten nicht vollständig gesetzt werden: {windows_result.get('error', 'Unbekannter Fehler')}\n",
            )

        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], check=False, capture_output=True)
        subprocess.Popen(["explorer.exe"])

        status_textbox.insert(
            "end",
            "ℹ️ Windows-Explorer wurde neu gestartet. Änderungen sollten nun sichtbar sein.\n",
        )
        status_textbox.see("end")
    except Exception as exc:
        status_textbox.insert("end", f"⚠️ Explorer-Neustart fehlgeschlagen: {exc}\n")
        status_textbox.see("end")
        messagebox.showerror(
            "Fehler beim Explorer-Neustart",
            f"Der Explorer konnte nicht neu gestartet werden:\n{exc}\n\n"
            "Bitte melden Sie sich am System ab und wieder an.",
        )
