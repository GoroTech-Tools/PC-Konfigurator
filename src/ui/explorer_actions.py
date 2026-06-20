from __future__ import annotations

import ctypes
import subprocess
import time
from tkinter import messagebox


def append_registry_restart_notice(status_textbox) -> None:
    """Hinweis für Anwender nach Registry-Anpassungen anzeigen."""
    notice = (
        "\nℹ️ Wichtiger Hinweis: Nach dem Anwenden der Registry-Einstellungen "
        "ist ein Neustart des Windows-Explorers oder eine Neuanmeldung am System empfohlen, "
        "damit alle Änderungen vollständig wirksam werden.\n"
    )
    status_textbox.insert("end", notice)


def _is_taskbar_visible() -> bool:
    """Prüft, ob die Windows-Taskleiste (Shell_TrayWnd) sichtbar ist."""
    try:
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        hwnd = user32.FindWindowW("Shell_TrayWnd", None)
        if not hwnd:
            return False
        return bool(user32.IsWindowVisible(hwnd))
    except Exception:
        return False


def _show_taskbar_if_present() -> bool:
    """Blendet die Taskleiste ein, falls das Fenster existiert, aber unsichtbar ist."""
    try:
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        hwnd = user32.FindWindowW("Shell_TrayWnd", None)
        if not hwnd:
            return False
        # 5 = SW_SHOW
        user32.ShowWindow(hwnd, 5)
        user32.SetForegroundWindow(hwnd)
        return bool(user32.IsWindowVisible(hwnd))
    except Exception:
        return False


def _restart_explorer_and_wait(timeout_seconds: float = 20.0) -> tuple[bool, str | None]:
    """Startet den Explorer neu und wartet, bis die Taskleiste wieder sichtbar ist."""
    subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], check=False, capture_output=True)

    # Detach über cmd/start verhindert, dass der Explorer am aufrufenden Prozess "hängt".
    subprocess.Popen(["cmd", "/c", "start", "", "explorer.exe"])

    deadline = time.monotonic() + max(1.0, float(timeout_seconds))
    while time.monotonic() < deadline:
        if _is_taskbar_visible():
            return True, None
        time.sleep(0.25)

    # Wenn die Taskbar existiert, aber versteckt ist, explizit sichtbar machen.
    if _show_taskbar_if_present() and _is_taskbar_visible():
        return True, None

    # Zweiter Startversuch, falls Explorer-Prozess läuft, aber Shell noch nicht angebunden ist.
    subprocess.Popen(["cmd", "/c", "start", "", "explorer.exe"])
    deadline2 = time.monotonic() + 8.0
    while time.monotonic() < deadline2:
        if _is_taskbar_visible():
            return True, None
        time.sleep(0.25)

    if _show_taskbar_if_present() and _is_taskbar_visible():
        return True, None

    # Harter Fallback: Shell-Komponenten neu initialisieren und userinit triggern.
    for proc in ("ShellExperienceHost", "StartMenuExperienceHost", "SearchHost"):
        subprocess.run(["taskkill", "/F", "/IM", f"{proc}.exe"], check=False, capture_output=True)

    subprocess.Popen(["cmd", "/c", "start", "", "explorer.exe"])
    subprocess.Popen(["cmd", "/c", "start", "", r"C:\Windows\System32\userinit.exe"])

    deadline3 = time.monotonic() + 12.0
    while time.monotonic() < deadline3:
        if _is_taskbar_visible() or _show_taskbar_if_present():
            return True, None
        time.sleep(0.25)

    return False, "Taskleiste blieb unsichtbar (auch nach Shell-Recovery/userinit-Fallback)"


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
        elif windows_result.get("warning"):
            status_textbox.insert(
                "end",
                f"ℹ️ Hinweis Windows-Einstellungen: {windows_result.get('warning')}\n",
            )

        ok, reason = _restart_explorer_and_wait(timeout_seconds=22.0)

        if ok:
            status_textbox.insert(
                "end",
                "ℹ️ Windows-Explorer wurde neu gestartet. Taskleiste/Desktop sind wieder verfügbar.\n",
            )
        else:
            status_textbox.insert(
                "end",
                "⚠️ Explorer wurde gestartet, aber die Taskleiste ist noch nicht sichtbar. "
                "Bitte 10–20 Sekunden warten oder sich einmal ab- und wieder anmelden.\n",
            )
            if reason:
                status_textbox.insert("end", f"ℹ️ Details: {reason}\n")

        status_textbox.see("end")
    except Exception as exc:
        status_textbox.insert("end", f"⚠️ Explorer-Neustart fehlgeschlagen: {exc}\n")
        status_textbox.see("end")
        messagebox.showerror(
            "Fehler beim Explorer-Neustart",
            f"Der Explorer konnte nicht neu gestartet werden:\n{exc}\n\n"
            "Bitte melden Sie sich am System ab und wieder an.",
        )
