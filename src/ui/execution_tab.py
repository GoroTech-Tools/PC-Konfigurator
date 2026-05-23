from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk


def build_execution_tab(
    tabview,
    *,
    on_run_full: Callable[[], None],
    on_run_office: Callable[[], None],
    on_restart_explorer: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den Ausführung-Tab und liefert relevante Widget-Referenzen zurück."""
    execution_frame = tabview.tab("Ausführung")

    ctk.CTkLabel(
        execution_frame,
        text="Konfiguration ausführen",
        font=ctk.CTkFont(size=18, weight="bold"),
    ).pack(pady=(12, 4))

    button_frame = ctk.CTkFrame(execution_frame)
    button_frame.pack(pady=(0, 10), padx=20, fill="x")

    ctk.CTkButton(
        button_frame,
        text="Vollständige Konfiguration starten",
        command=on_run_full,
        width=220,
        height=40,
        font=ctk.CTkFont(weight="bold"),
    ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

    ctk.CTkButton(
        button_frame,
        text="Nur Office konfigurieren",
        command=on_run_office,
        width=180,
        height=40,
    ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(
        execution_frame,
        text="Windows-Explorer neu starten",
        command=on_restart_explorer,
        width=260,
        height=34,
    ).pack(pady=(0, 8))

    ctk.CTkLabel(
        execution_frame,
        text="Status und Fortschritt:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=20, pady=(6, 4))

    progress_frame = ctk.CTkFrame(execution_frame)
    progress_frame.pack(fill="x", padx=20, pady=(0, 6))

    execution_state_label = ctk.CTkLabel(
        progress_frame,
        text="Bereit",
        font=ctk.CTkFont(weight="bold"),
        text_color="#1f6aa5",
        justify="left",
    )
    execution_state_label.pack(anchor="w", padx=10, pady=(8, 2))

    execution_progress = ctk.CTkProgressBar(progress_frame)
    execution_progress.pack(fill="x", padx=10, pady=(2, 6))
    execution_progress.set(0)

    execution_steps_label = ctk.CTkLabel(
        progress_frame,
        text="☐ Bereit",
        justify="left",
        anchor="w",
    )
    execution_steps_label.pack(anchor="w", padx=10, pady=(0, 10))

    execution_status = ctk.CTkTextbox(
        execution_frame,
        height=380,
        font=ctk.CTkFont(family="Consolas", size=12),
    )
    execution_status.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    initial_status = """🚀 PC-KONFIGURATOR - BEREIT ZUR AUSFÜHRUNG
==================================================

ℹ️ Anweisungen:
  • 'Vollständige Konfiguration starten' → Komplette Einrichtung
  • 'Nur Office konfigurieren' → Schnelle Registry-Optimierungen

📊 Der detaillierte Fortschritt wird hier live angezeigt.

🔴 Warten auf Benutzeraktion...
"""
    execution_status.insert("0.0", initial_status)

    return {
        "execution_state_label": execution_state_label,
        "execution_progress": execution_progress,
        "execution_steps_label": execution_steps_label,
        "execution_status": execution_status,
    }
