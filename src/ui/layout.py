from __future__ import annotations

from typing import Iterable

import customtkinter as ctk

TAB_OVERVIEW = "Übersicht"
TAB_START = "Start"
TAB_CONFIG = "Vorlagen/Ablage"
TAB_REGISTRY = "Registry"
TAB_EXECUTION = "Ausführung"
TAB_LOGS = "Logs"

DEFAULT_TABS = (
    TAB_OVERVIEW,
    TAB_START,
    TAB_CONFIG,
    TAB_REGISTRY,
    TAB_EXECUTION,
    TAB_LOGS,
)


def build_main_layout(
    root,
    *,
    title: str,
    tabs: Iterable[str] = DEFAULT_TABS,
):
    """Erstellt den gemeinsamen Hauptrahmen inklusive Tab-Container."""
    tabs = tuple(tabs)

    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(
        main_frame,
        text=title,
        font=ctk.CTkFont(size=24, weight="bold"),
    ).pack(pady=(10, 20))

    tabview = ctk.CTkTabview(main_frame)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    for tab_name in tabs:
        tabview.add(tab_name)

    return {
        "main_frame": main_frame,
        "tabview": tabview,
    }
