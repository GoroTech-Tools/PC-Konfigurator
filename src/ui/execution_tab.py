from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk

from ui.theme import create_scrollable_page, create_section_card


def build_execution_tab(
    tabview,
    *,
    advanced_mode: bool,
    on_run_full: Callable[[], None],
    on_run_office: Callable[[], None],
    on_restart_explorer: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den Ausführung-Tab und liefert relevante Widget-Referenzen zurück."""
    execution_frame = tabview.tab("Ausführung")

    page = create_scrollable_page(execution_frame)

    ctk.CTkLabel(
        page,
        text="Konfiguration ausführen",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(anchor="w", padx=8, pady=(2, 10))

    _actions_card, actions_body = create_section_card(
        page,
        title="Aktionen",
        description=(
            "Starten Sie die vollständige Einrichtung oder nur die Office-Konfiguration."
            if advanced_mode
            else "Starten Sie die vollständige Einrichtung."
        ),
    )

    button_frame = ctk.CTkFrame(actions_body)
    button_frame.pack(pady=(0, 8), padx=4, fill="x")

    run_full_button = ctk.CTkButton(
        button_frame,
        text="Vollständige Konfiguration starten",
        command=on_run_full,
        width=220,
        height=40,
        font=ctk.CTkFont(weight="bold"),
    )

    run_office_button = None
    if advanced_mode:
        run_office_button = ctk.CTkButton(
            button_frame,
            text="Nur Office konfigurieren",
            command=on_run_office,
            width=180,
            height=40,
        )

    def _layout_run_buttons(columns: int):
        cols = max(1, min(columns, 2 if run_office_button is not None else 1))
        run_full_button.grid_forget()
        if run_office_button is not None:
            run_office_button.grid_forget()
        if cols == 1 or run_office_button is None:
            run_full_button.grid(row=0, column=0, padx=4, pady=(4, 4), sticky="ew")
            if run_office_button is not None:
                run_office_button.grid(row=1, column=0, padx=4, pady=(4, 4), sticky="ew")
        else:
            run_full_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="ew")
            run_office_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="ew")
        for col in range(cols):
            button_frame.grid_columnconfigure(col, weight=1)

    def _on_button_frame_resize(event=None):
        width = 0
        try:
            width = int(button_frame.winfo_width())
        except Exception:
            width = 0
        _layout_run_buttons(1 if width < 620 else 2)

    _on_button_frame_resize()
    button_frame.bind("<Configure>", _on_button_frame_resize, add="+")

    ctk.CTkButton(
        actions_body,
        text="Windows-Explorer neu starten",
        command=on_restart_explorer,
        width=260,
        height=34,
    ).pack(anchor="w", padx=4, pady=(0, 2))

    _status_card, status_body = create_section_card(
        page,
        title="Status und Fortschritt",
        description="Der Laufstatus und die Detailmeldungen werden hier live aktualisiert.",
    )

    ctk.CTkLabel(
        status_body,
        text="Laufstatus:",
        font=ctk.CTkFont(weight="bold"),
    ).pack(anchor="w", padx=4, pady=(2, 4))

    progress_frame = ctk.CTkFrame(status_body)
    progress_frame.pack(fill="x", padx=4, pady=(0, 8))

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
        status_body,
        height=380,
        font=ctk.CTkFont(family="Consolas", size=12),
    )
    execution_status.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    initial_status = """🚀 PC-KONFIGURATOR - BEREIT ZUR AUSFÜHRUNG
==================================================

ℹ️ Anweisungen:
  • 'Vollständige Konfiguration starten' → Komplette Einrichtung
    • 'Nur Office konfigurieren' → Schnelle Registry-Optimierungen

📊 Der detaillierte Fortschritt wird hier live angezeigt.

🔴 Warten auf Benutzeraktion...
"""
    if not advanced_mode:
        initial_status = initial_status.replace("  • 'Nur Office konfigurieren' → Schnelle Registry-Optimierungen\n", "")
    execution_status.insert("0.0", initial_status)

    return {
        "execution_state_label": execution_state_label,
        "execution_progress": execution_progress,
        "execution_steps_label": execution_steps_label,
        "execution_status": execution_status,
    }
