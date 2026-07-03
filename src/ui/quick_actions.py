from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ui.theme import PALE_BUTTON_STYLE


def build_quick_actions_bar(
    parent,
    *,
    appearance_values: list[str],
    appearance_variable,
    on_appearance_changed: Callable[[str], None],
    on_open_start: Callable[[], None],
    on_open_config: Callable[[], None],
    on_open_execution: Callable[[], None],
    on_open_logs: Callable[[], None],
    on_run_full: Callable[[], None],
):
    """Erstellt eine kompakte Schnellzugriffsleiste mit Theme-Umschalter."""
    bar = ctk.CTkFrame(parent, corner_radius=10)
    bar.pack(fill="x", padx=10, pady=(0, 10))

    title = ctk.CTkLabel(
        bar,
        text="Schnellzugriff",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    title.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")

    actions_frame = ctk.CTkFrame(bar, fg_color="transparent")
    actions_frame.grid(row=0, column=1, padx=4, pady=6, sticky="ew")
    bar.grid_columnconfigure(1, weight=1)

    action_specs = [
        ("🏠 Start", on_open_start),
        ("🧩 Konfiguration", on_open_config),
        ("▶️ Ausführung", on_open_execution),
        ("📝 Logs", on_open_logs),
        ("🚀 Vollstart", on_run_full),
    ]

    action_buttons: list[ctk.CTkButton] = []
    for text, command in action_specs:
        btn = ctk.CTkButton(
            actions_frame,
            text=text,
            command=command,
            height=34,
            **PALE_BUTTON_STYLE,
        )
        btn._skip_uniform_size = True  # type: ignore[attr-defined]
        action_buttons.append(btn)

    def _render_actions(columns: int):
        cols = max(1, min(columns, len(action_buttons)))
        for idx, btn in enumerate(action_buttons):
            row = idx // cols
            col = idx % cols
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")

        for col in range(cols):
            actions_frame.grid_columnconfigure(col, weight=1)

    def _on_resize(event=None):
        width = 0
        try:
            width = int(actions_frame.winfo_width())
        except Exception:
            width = 0

        if width < 500:
            cols = 1
        elif width < 860:
            cols = 2
        elif width < 1180:
            cols = 3
        else:
            cols = 5

        for child in action_buttons:
            try:
                child.grid_forget()
            except Exception:
                pass
        _render_actions(cols)

    _on_resize()
    actions_frame.bind("<Configure>", _on_resize, add="+")

    right_side = ctk.CTkFrame(bar, fg_color="transparent")
    right_side.grid(row=0, column=2, padx=(8, 12), pady=8, sticky="e")

    ctk.CTkLabel(right_side, text="Design:").pack(side="left", padx=(0, 6))
    appearance_menu = ctk.CTkOptionMenu(
        right_side,
        values=appearance_values,
        variable=appearance_variable,
        command=on_appearance_changed,
        width=120,
    )
    appearance_menu.pack(side="left")

    return {
        "bar": bar,
        "appearance_menu": appearance_menu,
    }