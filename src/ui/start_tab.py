from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk


def build_start_tab(
    tabview,
    *,
    version: str,
    on_open_config: Callable[[], None],
    on_open_registry_info: Callable[[], None],
    on_run_full: Callable[[], None],
    on_run_office: Callable[[], None],
    on_check_system: Callable[[], None],
    on_restart_explorer: Callable[[], None],
    on_open_folder_templates: Callable[[], None],
    on_open_folder_fonts: Callable[[], None],
    on_open_folder_docs: Callable[[], None],
    on_open_folder_logs: Callable[[], None],
    on_open_doc_user: Callable[[], None],
    on_open_doc_tech: Callable[[], None],
    on_show_execution: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den AP1-ähnlichen Start-Tab und gibt relevante Widget-Referenzen zurück."""
    start_frame = tabview.tab("Start")

    ctk.CTkLabel(
        start_frame,
        text=f"PC-Konfigurator • v{version}",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(anchor="w", padx=16, pady=(14, 8))

    config_box = ctk.CTkFrame(start_frame)
    config_box.pack(fill="x", padx=12, pady=(0, 8))
    ctk.CTkLabel(config_box, text="Konfiguration", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
    ctk.CTkLabel(
        config_box,
        text="Schriftarten, Zielpfad und Template-Optionen bearbeiten Sie im Tab 'Vorlagen/Ablage'.",
        justify="left",
    ).pack(anchor="w", padx=12, pady=(0, 8))

    config_actions = ctk.CTkFrame(config_box)
    config_actions.pack(fill="x", padx=12, pady=(0, 10))
    ctk.CTkButton(config_actions, text="Konfiguration öffnen", command=on_open_config).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(config_actions, text="Registry-Info öffnen", command=on_open_registry_info).pack(side="left", padx=(0, 8), pady=6)

    action_box = ctk.CTkFrame(start_frame)
    action_box.pack(fill="x", padx=12, pady=(0, 8))
    ctk.CTkLabel(action_box, text="Aktionen", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))

    action_row = ctk.CTkFrame(action_box)
    action_row.pack(fill="x", padx=12, pady=(0, 10))
    ctk.CTkButton(
        action_row,
        text="Vollständige Konfiguration starten",
        command=on_run_full,
        font=ctk.CTkFont(weight="bold"),
        height=38,
    ).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(action_row, text="Nur Office konfigurieren", command=on_run_office, height=38).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(action_row, text="System prüfen", command=on_check_system, height=38).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(action_row, text="Explorer neu starten", command=on_restart_explorer, height=38).pack(side="left", pady=6)

    access_box = ctk.CTkFrame(start_frame)
    access_box.pack(fill="x", padx=12, pady=(0, 8))
    ctk.CTkLabel(access_box, text="Ordner & Dokumentation", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))

    folder_row = ctk.CTkFrame(access_box)
    folder_row.pack(fill="x", padx=12, pady=(0, 6))
    ctk.CTkButton(folder_row, text="Datei-Vorlagen", command=on_open_folder_templates).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(folder_row, text="Fonts", command=on_open_folder_fonts).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(folder_row, text="Dokumentation", command=on_open_folder_docs).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(folder_row, text="Logs", command=on_open_folder_logs).pack(side="left", pady=6)

    docs_row = ctk.CTkFrame(access_box)
    docs_row.pack(fill="x", padx=12, pady=(0, 10))
    ctk.CTkButton(docs_row, text="Anwender-Doku", command=on_open_doc_user).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(docs_row, text="Technik-Doku", command=on_open_doc_tech).pack(side="left", padx=(0, 8), pady=6)
    ctk.CTkButton(docs_row, text="Ausführung anzeigen", command=on_show_execution).pack(side="left", pady=6)

    return {}
