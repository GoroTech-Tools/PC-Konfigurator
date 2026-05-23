from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk


def build_overview_tab(tabview, *, on_check_system: Callable[[], None]) -> dict[str, Any]:
    """Erzeugt den Übersicht-Tab und liefert benötigte Widget-Referenzen."""
    overview_frame = tabview.tab("Übersicht")

    ctk.CTkLabel(
        overview_frame,
        text="Willkommen beim PC-Konfigurator!",
        font=ctk.CTkFont(size=18, weight="bold"),
    ).pack(anchor="w", padx=22, pady=(10, 0))

    ctk.CTkLabel(
        overview_frame,
        text="Diese Anwendung hilft Ihnen dabei, Ihren Windows-PC optimal für die Arbeit mit Office-Programmen zu konfigurieren.",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkLabel(
        overview_frame,
        text="VERFÜGBARE FUNKTIONEN:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=22, pady=(5, 0))
    ctk.CTkLabel(
        overview_frame,
        text="• Datei-Vorlagen automatisch synchronisieren\n"
             "• Office-Programme konfigurieren (Autokorrektur, Schriftarten, Pfade etc.)\n"
             "• Windows-Explorer-Einstellungen optimieren\n"
             "• Custom-Fonts installieren (Aptos, Montserrat, PT Sans etc.)",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkLabel(
        overview_frame,
        text="SO STARTEN SIE:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=22, pady=(5, 0))
    ctk.CTkLabel(
        overview_frame,
        text="1. Tab 'Konfiguration' → Einstellungen nach Ihren Wünschen anpassen\n"
             "2. Tab 'Registry-Info' → Geplante Änderungen einsehen (optional)\n"
             "3. Tab 'Ausführung' → Konfiguration starten",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkLabel(
        overview_frame,
        text="VOR DER AUSFÜHRUNG:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=22, pady=(5, 0))
    ctk.CTkLabel(
        overview_frame,
        text="• Speichern Sie alle offenen Office-Dateien\n\nKlicken Sie auf den Reiter 'Konfiguration', um die Einstellungen anzupassen.",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    status_frame = ctk.CTkFrame(overview_frame)
    status_frame.pack(fill="x", padx=10, pady=(0, 10))

    ctk.CTkLabel(status_frame, text="System-Status:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

    status_label = ctk.CTkLabel(
        status_frame,
        text="Klicken Sie auf 'System prüfen' um Ihre Windows- und Office-Version zu ermitteln.",
        justify="left",
    )
    status_label.pack(anchor="w", padx=20, pady=(0, 10))

    ctk.CTkButton(status_frame, text="System prüfen", command=on_check_system).pack(pady=10)

    return {
        "status_label": status_label,
    }
