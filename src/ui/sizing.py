from __future__ import annotations

import customtkinter as ctk


DEFAULT_BUTTON_WIDTH = 220
DEFAULT_BUTTON_HEIGHT = 38
DEFAULT_TAB_BUTTON_WIDTH = 220
DEFAULT_TAB_BUTTON_HEIGHT = 34


def _get_segmented_button(tabview):
    return getattr(tabview, "_segmented_button", None)


def _get_tab_button_count(tabview) -> int:
    segmented_button = _get_segmented_button(tabview)
    if segmented_button is None:
        return 0

    buttons_dict = getattr(segmented_button, "_buttons_dict", None)
    if isinstance(buttons_dict, dict):
        return len(buttons_dict)

    tabs = getattr(tabview, "_tab_dict", None)
    if isinstance(tabs, dict):
        return len(tabs)

    return 0


def _apply_tab_button_sizes(tabview, *, button_width: int, button_height: int) -> None:
    segmented_button = _get_segmented_button(tabview)
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
    _apply_tab_button_sizes(tabview, button_width=button_width, button_height=button_height)


def bind_dynamic_tab_sizes(
    tabview,
    *,
    bind_to=None,
    min_button_width: int = 120,
    max_button_width: int = 260,
    button_height: int = DEFAULT_TAB_BUTTON_HEIGHT,
    extra_padding: int = 24,
) -> None:
    """Passt die Tab-Schaltflächenbreite dynamisch an die verfügbare Fensterbreite an."""
    if getattr(tabview, "_dynamic_tab_size_bound", False):
        return

    bound_widget = bind_to or tabview
    tabview._dynamic_tab_size_bound = True  # type: ignore[attr-defined]
    tabview._dynamic_tab_size_job = None  # type: ignore[attr-defined]

    def _update_tab_sizes() -> None:
        segmented_button = _get_segmented_button(tabview)
        if segmented_button is None:
            return

        tab_count = _get_tab_button_count(tabview)
        if tab_count <= 0:
            return

        available_width = 0
        for candidate in (
            getattr(tabview, "winfo_width", lambda: 0)(),
            getattr(bound_widget, "winfo_width", lambda: 0)(),
            getattr(tabview.winfo_toplevel(), "winfo_width", lambda: 0)(),
        ):
            try:
                candidate_width = int(candidate)
            except Exception:
                continue
            if candidate_width > 1:
                available_width = candidate_width
                break

        if available_width <= 1:
            return

        usable_width = max(0, available_width - extra_padding)
        button_width = max(min_button_width, usable_width // tab_count)
        if max_button_width > 0:
            button_width = min(max_button_width, button_width)

        _apply_tab_button_sizes(
            tabview,
            button_width=button_width,
            button_height=button_height,
        )

    def _schedule_update(_event=None) -> None:
        job = getattr(tabview, "_dynamic_tab_size_job", None)
        if job is not None:
            try:
                tabview.after_cancel(job)
            except Exception:
                pass

        try:
            tabview._dynamic_tab_size_job = tabview.after(50, _update_tab_sizes)  # type: ignore[attr-defined]
        except Exception:
            _update_tab_sizes()

    try:
        bound_widget.bind("<Configure>", _schedule_update, add="+")
    except Exception:
        pass

    try:
        tabview.after(100, _update_tab_sizes)
    except Exception:
        _update_tab_sizes()
