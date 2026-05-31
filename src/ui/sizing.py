from __future__ import annotations

import customtkinter as ctk


DEFAULT_BUTTON_WIDTH = 220
DEFAULT_BUTTON_HEIGHT = 38
DEFAULT_TAB_BUTTON_WIDTH = 170
DEFAULT_TAB_BUTTON_HEIGHT = 34


def apply_uniform_button_sizes(container, *, width: int = DEFAULT_BUTTON_WIDTH, height: int = DEFAULT_BUTTON_HEIGHT) -> None:
    """Setzt rekursiv eine einheitliche Größe für alle CTkButtons unterhalb eines Containers."""
    try:
        children = container.winfo_children()
    except Exception:
        return

    for child in children:
        try:
            if isinstance(child, ctk.CTkButton):
                child.configure(width=width, height=height)
        except Exception:
            pass
        apply_uniform_button_sizes(child, width=width, height=height)


def apply_uniform_tab_sizes(
    tabview,
    *,
    button_width: int = DEFAULT_TAB_BUTTON_WIDTH,
    button_height: int = DEFAULT_TAB_BUTTON_HEIGHT,
) -> None:
    """Setzt bei CTkTabview gleich große Tab-Schaltflächen (Segmented-Buttons)."""
    segmented_button = getattr(tabview, "_segmented_button", None)
    if segmented_button is None:
        return

    try:
        segmented_button.configure(dynamic_resizing=False, height=button_height)
    except Exception:
        pass

    buttons_dict = getattr(segmented_button, "_buttons_dict", None)
    if isinstance(buttons_dict, dict):
        for button in buttons_dict.values():
            try:
                button.configure(width=button_width, height=button_height)
            except Exception:
                pass
