from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk

from ui.theme import CONTINUE_BUTTON_STYLE, PALE_BUTTON_STYLE, PAGE_HEADING_COLOR, create_scrollable_page, create_section_card


def build_start_tab(
    tabview,
    *,
    ui_mode_var,
    advanced_mode: bool,
    current_startmenu_mode_text: str,
    on_ui_mode_changed: Callable[[], None],
    on_open_config: Callable[[], None],
    on_open_registry_info: Callable[[], None],
    on_open_folder_templates: Callable[[], None],
    on_open_folder_fonts: Callable[[], None],
    on_open_folder_logs: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den AP1-ähnlichen Start-Tab und gibt relevante Widget-Referenzen zurück."""
    start_frame = tabview.tab("Start")

    page = create_scrollable_page(start_frame)

    ctk.CTkLabel(
        page,
        text="Willkommen im PC-Konfigurator",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=PAGE_HEADING_COLOR,
        fg_color="transparent",
    ).pack(anchor="w", padx=8, pady=(2, 10))

    _mode_card, mode_body = create_section_card(
        page,
        title="Bedienmodus",
        description="Einfach für Standardabläufe, Erweitert für zusätzliche Diagnose- und Wartungsfunktionen.",
    )
    mode_row = ctk.CTkFrame(mode_body, fg_color="transparent")
    mode_row.pack(fill="x", padx=4, pady=(0, 2))
    ctk.CTkRadioButton(mode_row, text="Einfach", variable=ui_mode_var, value="simple", command=on_ui_mode_changed).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkRadioButton(mode_row, text="Erweitert", variable=ui_mode_var, value="advanced", command=on_ui_mode_changed).pack(side="left", pady=6)

    _config_card, config_body = create_section_card(
        page,
        title="Konfiguration",
        description="Im Tab 'Konfiguration' legen Sie alle Einstellungen für den vollständigen Konfigurationslauf fest.",
    )
    ctk.CTkLabel(
        config_body,
        text=(
            "Dort können Sie unter anderem folgende Einstellungen anpassen:\n"
            "• Zielverzeichnis für Datei-Vorlagen (umgeleitetes Dokumente-Verzeichnis oder Laufwerk)\n"
            "• Corporate Design und Schriftart\n"
            "• Schriftgrößen für Word, Outlook und Excel\n"
            "• Anzeige ausgeblendeter Elemente und Taskleisten-Ausrichtung\n"
            "• Im erweiterten Modus zusätzlich COM-Synchronisierung, Office-Preclose, Warm-up und Firmenmodus"
        ),
        justify="left",
        anchor="w",
        wraplength=980,
    ).pack(anchor="w", padx=4, pady=(0, 8))

    _close_apps_card, close_apps_body = create_section_card(
        page,
        title="Wichtiger Hinweis vor der Ausführung",
        description="Vor dem Start müssen alle Anwendungen geschlossen sein, auf deren Benutzerdateien der PC-Konfigurator zugreift.",
    )
    ctk.CTkLabel(
        close_apps_body,
        text=(
            "Bitte beenden Sie Microsoft Edge, Microsoft Outlook, Microsoft Excel und Microsoft Word vollständig, "
            "bevor Sie die vollständige Konfiguration starten. Dies verhindert gesperrte Profil-, Template- und Signaturdateien."
        ),
        justify="left",
        anchor="w",
        wraplength=980,
    ).pack(anchor="w", padx=4, pady=(0, 8))

    startmenu_mode_label = ctk.CTkLabel(
        config_body,
        text=f"Aktueller Kontextmenü-Modus: {current_startmenu_mode_text}",
        justify="left",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=("#2F3B52", "#D0DBF0"),
    )
    startmenu_mode_label.pack(anchor="w", padx=4, pady=(0, 8))

    config_actions = ctk.CTkFrame(config_body, fg_color="transparent")
    config_actions.pack(fill="x", padx=4, pady=(0, 2))

    left_actions = ctk.CTkFrame(config_actions, fg_color="transparent")
    left_actions.pack(side="left", fill="x", expand=True)

    right_actions = ctk.CTkFrame(config_actions, fg_color="transparent")
    right_actions.pack(side="right")

    next_button = ctk.CTkButton(
        right_actions,
        text="Weiter",
        command=on_open_config,
        font=ctk.CTkFont(weight="bold"),
        width=220,
        height=38,
        **CONTINUE_BUTTON_STYLE,
    )
    next_button.pack(side="right", pady=6)

    registry_info_button = None
    if advanced_mode:
        registry_info_button = ctk.CTkButton(left_actions, text="Registry-Info öffnen", command=on_open_registry_info, **PALE_BUTTON_STYLE)
        registry_info_button.pack(side="left", padx=(0, 8), pady=6)

    if advanced_mode:
        _access_card, access_body = create_section_card(
            page,
            title="Ausgangsmaterial",
            description="Direktzugriff auf häufig genutzte Arbeitsordner.",
        )

        folder_row = ctk.CTkFrame(access_body, fg_color="transparent")
        folder_row.pack(fill="x", padx=4, pady=(0, 2))
        folder_buttons: list[ctk.CTkButton] = [
            ctk.CTkButton(folder_row, text="Datei-Vorlagen", command=on_open_folder_templates, **PALE_BUTTON_STYLE),
            ctk.CTkButton(folder_row, text="Fonts", command=on_open_folder_fonts, **PALE_BUTTON_STYLE),
            ctk.CTkButton(folder_row, text="Logs", command=on_open_folder_logs, **PALE_BUTTON_STYLE),
        ]

        def _layout_folder_buttons(columns: int):
            cols = max(1, min(columns, len(folder_buttons)))
            for idx, button in enumerate(folder_buttons):
                row = idx // cols
                col = idx % cols
                button.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            for col in range(cols):
                folder_row.grid_columnconfigure(col, weight=1)

        def _on_folder_row_resize(event=None):
            width = 0
            try:
                width = int(folder_row.winfo_width())
            except Exception:
                width = 0

            cols = 1 if width < 520 else 3
            for button in folder_buttons:
                try:
                    button.grid_forget()
                except Exception:
                    pass
            _layout_folder_buttons(cols)

        _on_folder_row_resize()
        folder_row.bind("<Configure>", _on_folder_row_resize, add="+")

    return {
        "startmenu_mode_label": startmenu_mode_label,
        "registry_info_button": registry_info_button,
    }
