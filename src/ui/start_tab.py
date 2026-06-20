from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk


def build_start_tab(
    tabview,
    *,
    ui_mode_var,
    advanced_mode: bool,
    current_startmenu_mode_text: str,
    on_ui_mode_changed: Callable[[], None],
    on_open_config: Callable[[], None],
    on_open_registry_info: Callable[[], None],
    on_run_full: Callable[[], None],
    on_run_office: Callable[[], None],
    on_check_system: Callable[[], None],
    on_restart_explorer: Callable[[], None],
    on_open_folder_templates: Callable[[], None],
    on_open_folder_fonts: Callable[[], None],
    on_open_folder_logs: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den AP1-ähnlichen Start-Tab und gibt relevante Widget-Referenzen zurück."""
    start_frame = tabview.tab("Start")

    pale_button_style = {
        "fg_color": ("#DCE3EA", "#4A5562"),
        "hover_color": ("#CBD4DE", "#5A6674"),
        "text_color": ("#253040", "#ECF1F7"),
        "border_width": 1,
        "border_color": ("#B8C3CF", "#6A7683"),
    }

    mode_box = ctk.CTkFrame(start_frame)
    mode_box.pack(fill="x", padx=12, pady=(10, 8))
    ctk.CTkLabel(mode_box, text="Bedienmodus", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
    mode_row = ctk.CTkFrame(mode_box)
    mode_row.pack(fill="x", padx=12, pady=(0, 10))
    ctk.CTkRadioButton(mode_row, text="Einfach", variable=ui_mode_var, value="simple", command=on_ui_mode_changed).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkRadioButton(mode_row, text="Erweitert", variable=ui_mode_var, value="advanced", command=on_ui_mode_changed).pack(side="left", pady=6)

    config_box = ctk.CTkFrame(start_frame)
    config_box.pack(fill="x", padx=12, pady=(0, 8))
    ctk.CTkLabel(config_box, text="Konfiguration", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
    ctk.CTkLabel(
        config_box,
        text="Schriftarten, Zielpfad und Template-Optionen bearbeiten Sie im Tab 'Vorlagen/Ablage'.",
        justify="left",
    ).pack(anchor="w", padx=12, pady=(0, 8))

    startmenu_mode_label = ctk.CTkLabel(
        config_box,
        text=f"Aktueller Startmenü-Modus: {current_startmenu_mode_text}",
        justify="left",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=("#2F3B52", "#D0DBF0"),
    )
    startmenu_mode_label.pack(anchor="w", padx=12, pady=(0, 8))

    config_actions = ctk.CTkFrame(config_box)
    config_actions.pack(fill="x", padx=12, pady=(0, 10))
    ctk.CTkButton(config_actions, text="Konfiguration öffnen", command=on_open_config, **pale_button_style).pack(side="left", padx=(0, 8), pady=6)
    registry_info_button = None
    if advanced_mode:
        registry_info_button = ctk.CTkButton(config_actions, text="Registry-Info öffnen", command=on_open_registry_info, **pale_button_style)
        registry_info_button.pack(side="left", padx=(0, 8), pady=6)

    action_box = ctk.CTkFrame(start_frame)
    action_box.pack(fill="x", padx=12, pady=(0, 8))
    ctk.CTkLabel(action_box, text="Aktionen", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
    details_hint = (
        "Für Details konsultieren Sie bitte die Tabs 'Vorlagen/Ablage' und Registry."
        if advanced_mode
        else "Für Details konsultieren Sie bitte den Tab 'Vorlagen/Ablage'."
    )
    ctk.CTkLabel(
        action_box,
        text="Hier können die empfohlenen Standardeinstellungen direkt gestartet werden. "
             f"{details_hint}",
        justify="left",
    ).pack(anchor="w", padx=12, pady=(0, 8))

    ctk.CTkLabel(
        action_box,
        text="SO STARTEN SIE:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=12, pady=(2, 0))
    action_steps_text = (
        "1. Tab 'Vorlagen/Ablage' → Schriftart, Zielpfad und Template-Optionen anpassen\n"
        "2. Tab 'Registry' → Geplante Änderungen einsehen (optional)\n"
        "3. Über die Aktionen unten die Konfiguration starten"
        if advanced_mode
        else
        "1. Tab 'Vorlagen/Ablage' → Schriftart, Zielpfad und Template-Optionen anpassen\n"
        "2. Über die Aktionen unten die Konfiguration starten"
    )
    ctk.CTkLabel(
        action_box,
        text=action_steps_text,
        justify="left",
    ).pack(anchor="w", padx=12, pady=(0, 8))

    ctk.CTkLabel(
        action_box,
        text="VOR DER AUSFÜHRUNG:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=12, pady=(2, 0))
    ctk.CTkLabel(
        action_box,
        text="• Speichern Sie alle offenen Office-Dateien.",
        justify="left",
    ).pack(anchor="w", padx=12, pady=(0, 8))

    action_row = ctk.CTkFrame(action_box)
    action_row.pack(fill="x", padx=12, pady=(0, 10))
    ctk.CTkButton(
        action_row,
        text="Vollständige Konfiguration starten",
        command=on_run_full,
        font=ctk.CTkFont(weight="bold"),
        height=38,
        **pale_button_style,
    ).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(action_row, text="Nur Office konfigurieren", command=on_run_office, height=38, **pale_button_style).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(action_row, text="System prüfen", command=on_check_system, height=38, **pale_button_style).pack(side="left", padx=(0, 8), pady=6)
    explorer_button = None
    if advanced_mode:
        explorer_button = ctk.CTkButton(action_row, text="Explorer neu starten", command=on_restart_explorer, height=38, **pale_button_style)
        explorer_button.pack(side="left", pady=6)

    if advanced_mode:
        access_box = ctk.CTkFrame(start_frame)
        access_box.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(access_box, text="Ausgangsmaterial", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))

        folder_row = ctk.CTkFrame(access_box)
        folder_row.pack(fill="x", padx=12, pady=(0, 6))
        ctk.CTkButton(folder_row, text="Datei-Vorlagen", command=on_open_folder_templates, **pale_button_style).pack(side="left", padx=(0, 8), pady=6)
        ctk.CTkButton(folder_row, text="Fonts", command=on_open_folder_fonts, **pale_button_style).pack(side="left", padx=(0, 8), pady=6)
        ctk.CTkButton(folder_row, text="Logs", command=on_open_folder_logs, **pale_button_style).pack(side="left", pady=6)

    return {
        "startmenu_mode_label": startmenu_mode_label,
        "registry_info_button": registry_info_button,
        "explorer_button": explorer_button,
    }
