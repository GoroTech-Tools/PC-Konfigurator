from __future__ import annotations

from typing import Callable

import customtkinter as ctk


def build_registry_info_tab(tabview, *, on_open_registry_details: Callable[[], None]) -> None:
    """Erzeugt den Registry-Info-Tab."""
    registry_frame = tabview.tab("Registry")

    ctk.CTkLabel(
        registry_frame,
        text="Registry-Einstellungen Übersicht",
        font=ctk.CTkFont(size=16, weight="bold"),
    ).pack(pady=10)

    ctk.CTkLabel(
        registry_frame,
        text="WAS PASSIERT:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=22, pady=(5, 0))
    ctk.CTkLabel(
        registry_frame,
        text="Diese Anwendung nimmt verschiedene Registry-Einstellungen für Office-Programme und Windows-System vor. Alle Änderungen werden detailliert dokumentiert und sind vollständig transparent.",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkLabel(
        registry_frame,
        text="SICHERHEIT:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=22, pady=(5, 0))
    ctk.CTkLabel(
        registry_frame,
        text="• Alle Änderungen sind reversibel\n• Nur HKEY_CURRENT_USER wird modifiziert (sicher für Benutzer)\n• Keine Systemdateien werden verändert",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkLabel(
        registry_frame,
        text="ÜBERSICHT DER EINSTELLUNGSKATEGORIEN:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=22, pady=(5, 0))
    ctk.CTkLabel(
        registry_frame,
        text=(
            "• Word - Benutzeroberfläche (Entwicklertools, Lineal)\n"
            "• Word - Formatierung (Formatierungszeichen, Tabellen)\n"
            "• Word - Datei-Vorlagen (DOT-PATH, STARTUP-PATH für Normal.dotm)\n"
            "• Word - Dateipfade und Schriftarten\n"
            "• Word - Autokorrektur-Einstellungen\n"
            "• Excel - Datei-Vorlagen (XLSTART-Info für Mappe.xltx)\n"
            "• Excel - Dateipfade und Schriftarten\n"
            "• Office - Allgemeine Einstellungen\n"
            "• Windows - Taskleiste und Kontextmenü"
        ),
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkLabel(
        registry_frame,
        text="Klicken Sie auf 'Detaillierte Ansicht öffnen' um alle geplanten Einstellungen mit ausführlichen Beschreibungen zu sehen.",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=22, pady=(0, 8))

    ctk.CTkButton(
        registry_frame,
        text="Detaillierte Ansicht öffnen",
        command=on_open_registry_details,
        font=ctk.CTkFont(weight="bold"),
    ).pack(pady=(10, 20))
