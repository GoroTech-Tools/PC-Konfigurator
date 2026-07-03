from __future__ import annotations

from typing import Iterable

import customtkinter as ctk

from ui.theme import CARD_TITLE_COLOR

TAB_START = "Start"
TAB_CONFIG = "Konfiguration"
TAB_REGISTRY = "Registry"
TAB_EXECUTION = "Ausführung"
TAB_LOGS = "Logs"

DEFAULT_TABS = (
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

    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=(10, 8))

    ctk.CTkLabel(
        header_frame,
        text=title,
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(side="left", pady=(0, 0))

    tabview = ctk.CTkTabview(main_frame)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    for tab_name in tabs:
        tabview.add(tab_name)

    return {
        "main_frame": main_frame,
        "header_frame": header_frame,
        "tabview": tabview,
    }
