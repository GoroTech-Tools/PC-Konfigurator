from __future__ import annotations

import customtkinter as ctk


PALE_BUTTON_STYLE = {
    "fg_color": ("#DCE3EA", "#4A5562"),
    "hover_color": ("#CBD4DE", "#5A6674"),
    "text_color": ("#253040", "#ECF1F7"),
    "border_width": 1,
    "border_color": ("#B8C3CF", "#6A7683"),
}

STATUS_COLORS = {
    "info": ("#1F4E8C", "#8EC5FF"),
    "success": ("#1F7A3D", "#8EE6A9"),
    "warning": ("#8A4B00", "#FFC37A"),
    "error": ("#9F1239", "#FDA4AF"),
    "muted": ("#4B5563", "#D1D5DB"),
}


def get_status_color(kind: str):
    """Liefert die konsistente Textfarbe für semantische Statuszustände."""
    return STATUS_COLORS.get(kind, STATUS_COLORS["info"])


def create_scrollable_page(tab_frame):
    """Erzeugt einen standardisierten Scroll-Container für umfangreiche Tabs."""
    page = ctk.CTkScrollableFrame(tab_frame, fg_color="transparent")
    page.pack(fill="both", expand=True, padx=10, pady=10)
    return page


def create_section_card(parent, *, title: str, description: str | None = None):
    """Erzeugt eine einheitliche Inhaltskarte mit Titel und optionaler Beschreibung."""
    card = ctk.CTkFrame(parent, corner_radius=10)
    card.pack(fill="x", padx=4, pady=(0, 10))

    ctk.CTkLabel(
        card,
        text=title,
        font=ctk.CTkFont(size=15, weight="bold"),
    ).pack(anchor="w", padx=14, pady=(12, 4))

    if description:
        ctk.CTkLabel(
            card,
            text=description,
            justify="left",
            wraplength=980,
            text_color=("#4B5563", "#D1D5DB"),
        ).pack(anchor="w", padx=14, pady=(0, 8))

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="x", padx=12, pady=(0, 12))

    return card, body