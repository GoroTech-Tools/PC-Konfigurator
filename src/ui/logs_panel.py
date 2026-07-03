from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ui.theme import PAGE_HEADING_COLOR, create_scrollable_page, create_section_card


def build_logs_tab(
    tabview,
    *,
    tab_name: str,
    on_refresh,
    on_clear,
    on_save,
):
    """Erstellt den Logs-Tab und liefert Widget-Referenzen zurück."""
    logs_frame = tabview.tab(tab_name)

    page = create_scrollable_page(logs_frame)

    ctk.CTkLabel(
        page,
        text="Logs und Diagnose",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=PAGE_HEADING_COLOR,
        fg_color="transparent",
    ).pack(anchor="w", padx=8, pady=(2, 10))

    _logs_card, logs_body = create_section_card(
        page,
        title="Aktuelle Laufprotokolle",
        description="Es wird automatisch die neueste Log-Datei angezeigt.",
    )

    log_text = ctk.CTkTextbox(logs_body, height=420)
    log_text.pack(fill="both", expand=True, padx=4, pady=(0, 10))

    log_button_frame = ctk.CTkFrame(logs_body)
    log_button_frame.pack(fill="x", padx=4, pady=(0, 2))

    refresh_button = ctk.CTkButton(
        log_button_frame,
        text="Logs aktualisieren",
        command=on_refresh,
    )
    refresh_button.pack(side="left", padx=5)

    clear_button = ctk.CTkButton(
        log_button_frame,
        text="Logs löschen",
        command=on_clear,
    )
    clear_button.pack(side="left", padx=5)

    save_button = ctk.CTkButton(
        log_button_frame,
        text="Logs speichern",
        command=on_save,
    )
    save_button.pack(side="right", padx=5)

    return {
        "log_text": log_text,
    }


def refresh_logs_view(log_text, app_dir: Path, *, show_errors: bool = True) -> None:
    """Lädt die neueste Log-Datei in den Logs-Textbereich."""
    try:
        log_dir = app_dir / "logs"
        if not log_dir.exists():
            log_text.delete("0.0", "end")
            log_text.insert("0.0", "Keine Log-Dateien gefunden.")
            return

        log_files = list(log_dir.glob("*.log"))
        if not log_files:
            log_text.delete("0.0", "end")
            log_text.insert("0.0", "Keine Log-Dateien gefunden.")
            return

        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

        with open(latest_log, "r", encoding="utf-8") as f:
            content = f.read()

        log_text.delete("0.0", "end")
        log_text.insert("0.0", content)
        log_text.see("end")
    except Exception as exc:
        if show_errors:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Logs: {exc}")


def clear_logs_view(log_text) -> None:
    """Leert die Log-Anzeige."""
    log_text.delete("0.0", "end")


def save_logs_view(log_text) -> None:
    """Speichert den aktuellen Log-Text in eine Datei."""
    try:
        content = log_text.get("0.0", "end")
        if not content.strip():
            messagebox.showwarning("Warnung", "Keine Logs zum Speichern vorhanden.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log-Dateien", "*.log"), ("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")],
        )

        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            log_text.insert("end", f"\n[INFO] Logs gespeichert in: {filename}\n")
            log_text.see("end")
    except Exception as exc:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Logs: {exc}")
