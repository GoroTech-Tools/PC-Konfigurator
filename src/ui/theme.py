from __future__ import annotations

import customtkinter as ctk


PALE_BUTTON_STYLE = {
    "fg_color": ("#DCE3EA", "#4A5562"),
    "hover_color": ("#CBD4DE", "#5A6674"),
    "text_color": ("#253040", "#ECF1F7"),
    "border_width": 1,
    "border_color": ("#B8C3CF", "#6A7683"),
}

CONTINUE_BUTTON_STYLE = {
    "fg_color": ("#E8F1FF", "#1F2D44"),
    "hover_color": ("#D8E9FF", "#284061"),
    "text_color": ("#0F2A56", "#F3F7FF"),
    "border_width": 2,
    "border_color": ("#1D4ED8", "#60A5FA"),
}

CARD_STYLE = {
    "fg_color": ("#EEF2F7", "#121A26"),
    "border_width": 1,
    "border_color": ("#D5DEE8", "#364155"),
}

CARD_TITLE_COLOR = ("#0F172A", "#FFFFFF")
PAGE_HEADING_COLOR = ("#0B1F44", "#EAF2FF")

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


def create_section_card(parent, *, title: str, description: str | None = None, compact: bool = False):
    """Erzeugt eine einheitliche Inhaltskarte mit Titel und optionaler Beschreibung.

    ``compact=True`` verringert die Innen-/Außenabstände für platzkritische Tabs.
    """
    card_gap = 6 if compact else 10
    title_pady = (9, 3) if compact else (12, 4)
    desc_pady = (0, 5) if compact else (0, 8)
    body_pady = (0, 8) if compact else (0, 12)

    card = ctk.CTkFrame(parent, corner_radius=10, **CARD_STYLE)
    card.pack(fill="x", padx=4, pady=(0, card_gap))

    ctk.CTkLabel(
        card,
        text=title,
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=title_pady)

    if description:
        ctk.CTkLabel(
            card,
            text=description,
            justify="left",
            wraplength=980,
            text_color=("#4B5563", "#D1D5DB"),
        ).pack(anchor="w", padx=14, pady=desc_pady)

    body = ctk.CTkFrame(card, fg_color="transparent")
    body.pack(fill="x", padx=12, pady=body_pady)

    return card, body