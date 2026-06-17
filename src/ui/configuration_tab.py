from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk


def build_configuration_tab(
    tabview,
    *,
    use_documents_var,
    target_drive_var,
    startmenu_mode_var,
    font_name_var,
    font_size_word_var,
    font_size_excel_var,
    available_font_families: list[str],
) -> dict[str, Any]:
    """Erzeugt den Konfiguration-Tab und gibt benötigte Widget-Referenzen zurück."""
    config_frame = tabview.tab("Vorlagen/Ablage")

    main_frame = ctk.CTkFrame(config_frame)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    info_frame = ctk.CTkFrame(main_frame)
    info_frame.pack(fill="x", padx=10, pady=(5, 10))

    ctk.CTkLabel(
        info_frame,
        text="Konfigurationshinweise",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=10, pady=(8, 3))

    info_text = "Passen Sie die Einstellungen nach Ihren Bedürfnissen an. Alle Änderungen werden sicher in der Windows-Registry gespeichert."
    ctk.CTkLabel(info_frame, text=info_text, wraplength=900).pack(anchor="w", padx=10, pady=(0, 8))

    target_section = ctk.CTkFrame(main_frame)
    target_section.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(
        target_section,
        text="Zielverzeichnis für Datei-Vorlagen:",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=10, pady=(10, 0))

    ctk.CTkLabel(
        target_section,
        text="Wählen Sie, wo die Office-Vorlagen gespeichert werden sollen:",
        font=ctk.CTkFont(size=11),
        text_color="gray",
    ).pack(anchor="w", padx=10, pady=(0, 5))

    ctk.CTkRadioButton(
        target_section,
        text="Laufwerk verwenden:",
        variable=use_documents_var,
        value=False,
    ).pack(anchor="w", padx=20, pady=2)

    drive_frame = ctk.CTkFrame(target_section)
    drive_frame.pack(fill="x", padx=30, pady=(5, 10))

    ctk.CTkLabel(drive_frame, text="Laufwerksbuchstabe:").pack(side="left", padx=5)

    drive_options = [f"{chr(i)}:" for i in range(ord("Z"), ord("C") - 1, -1)]
    ctk.CTkOptionMenu(drive_frame, variable=target_drive_var, values=drive_options, width=80).pack(side="left", padx=5)

    ctk.CTkLabel(
        drive_frame,
        text="(Im BFW bitte das Laufwerk Z wählen.)",
        font=ctk.CTkFont(size=10),
        text_color="gray",
    ).pack(side="left", padx=10)

    ctk.CTkRadioButton(
        target_section,
        text="Dokumente-Verzeichnis verwenden",
        variable=use_documents_var,
        value=True,
    ).pack(anchor="w", padx=20, pady=(5, 15))

    startmenu_section = ctk.CTkFrame(main_frame)
    startmenu_section.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(
        startmenu_section,
        text="Startmenü-Modus:",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=10, pady=(10, 0))

    ctk.CTkLabel(
        startmenu_section,
        text="Wählen Sie, welcher Startmenü-Modus beim Start des PC-Konfigurators dauerhaft gesetzt werden soll.",
        font=ctk.CTkFont(size=11),
        text_color="gray",
    ).pack(anchor="w", padx=10, pady=(0, 5))

    ctk.CTkRadioButton(
        startmenu_section,
        text="Windows-11-Startmenü bevorzugen (empfohlen)",
        variable=startmenu_mode_var,
        value="win11",
    ).pack(anchor="w", padx=20, pady=2)

    ctk.CTkRadioButton(
        startmenu_section,
        text="Klassisches Startmenü dauerhaft aktivieren (Fallback)",
        variable=startmenu_mode_var,
        value="classic",
    ).pack(anchor="w", padx=20, pady=(2, 12))

    font_section = ctk.CTkFrame(main_frame)
    font_section.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(font_section, text="Schriftart-Konfiguration:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

    ctk.CTkLabel(
        font_section,
        text="Alle Schriften aus dem Ordner 'Fonts' werden automatisch im Benutzerprofil installiert. Die gewählte Schrift wird den Office-Vorlagen und der Registry zugewiesen:",
        font=ctk.CTkFont(size=11),
        text_color="gray",
    ).pack(anchor="w", padx=10, pady=(0, 5))

    font_frame = ctk.CTkFrame(font_section)
    font_frame.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(font_frame, text="Schriftart:").pack(anchor="w", padx=5)

    ctk.CTkOptionMenu(
        font_frame,
        variable=font_name_var,
        values=available_font_families,
    ).pack(anchor="w", padx=5, pady=5)

    size_frame = ctk.CTkFrame(font_section)
    size_frame.pack(fill="x", padx=20, pady=(0, 10))

    word_size_frame = ctk.CTkFrame(size_frame)
    word_size_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)

    ctk.CTkLabel(word_size_frame, text="Word/Outlook-Schriftgröße:").pack(anchor="w", padx=5)
    ctk.CTkOptionMenu(word_size_frame, variable=font_size_word_var, values=["10", "11", "12"]).pack(anchor="w", padx=5, pady=5)

    excel_size_frame = ctk.CTkFrame(size_frame)
    excel_size_frame.pack(side="right", fill="x", expand=True, padx=5, pady=5)

    ctk.CTkLabel(excel_size_frame, text="Excel-Schriftgröße:").pack(anchor="w", padx=5)
    ctk.CTkOptionMenu(excel_size_frame, variable=font_size_excel_var, values=["10", "11", "12"]).pack(anchor="w", padx=5, pady=5)

    return {}
