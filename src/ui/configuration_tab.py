from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk

from ui.theme import CARD_STYLE, CARD_TITLE_COLOR, CONTINUE_BUTTON_STYLE, PAGE_HEADING_COLOR, PALE_BUTTON_STYLE, create_scrollable_page, create_section_card


def build_configuration_tab(
    tabview,
    *,
    use_documents_var,
    target_drive_var,
    startmenu_mode_var,
    hidden_items_mode_var,
    enable_firm_mode_var,
    enable_com_sync_var,
    enable_office_preclose_var,
    enable_office_warmup_var,
    font_name_var,
    font_size_word_var,
    font_size_excel_var,
    available_font_families: list[str],
    on_continue_to_execution: Callable[[], None],
    on_open_font_preview: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den Konfiguration-Tab und gibt benötigte Widget-Referenzen zurück."""
    config_frame = tabview.tab("Konfiguration")

    page = create_scrollable_page(config_frame)

    ctk.CTkLabel(
        page,
        text="Einstellungen",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=PAGE_HEADING_COLOR,
        fg_color="transparent",
    ).pack(anchor="w", padx=8, pady=(2, 6))

    top_row = ctk.CTkFrame(page, fg_color="transparent")
    top_row.pack(fill="x", padx=4, pady=(0, 6))
    top_row.grid_columnconfigure(0, weight=1)
    top_row.grid_columnconfigure(1, weight=1)

    target_card = ctk.CTkFrame(top_row, corner_radius=10, **CARD_STYLE)
    target_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
    ctk.CTkLabel(
        target_card,
        text="Zielverzeichnis für Datei-Vorlagen",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))
    ctk.CTkLabel(
        target_card,
        text="Wählen Sie, wo Office-Vorlagen gespeichert werden sollen.",
        justify="left",
        wraplength=440,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))
    target_body = ctk.CTkFrame(target_card, fg_color="transparent")
    target_body.pack(fill="x", padx=12, pady=(0, 8))

    ctk.CTkRadioButton(
        target_body,
        text="Laufwerk verwenden:",
        variable=use_documents_var,
        value=False,
    ).pack(anchor="w", padx=6, pady=2)

    drive_frame = ctk.CTkFrame(target_body)
    drive_frame.pack(fill="x", padx=6, pady=(4, 8))

    ctk.CTkLabel(drive_frame, text="Laufwerksbuchstabe:").pack(side="left", padx=5)

    drive_options = [f"{chr(i)}:" for i in range(ord("Z"), ord("C") - 1, -1)]
    ctk.CTkOptionMenu(drive_frame, variable=target_drive_var, values=drive_options, width=80).pack(side="left", padx=5)

    ctk.CTkLabel(
        drive_frame,
        text="(Im BFW bitte das Laufwerk Z wählen.)",
        font=ctk.CTkFont(size=10),
        text_color="gray",
    ).pack(side="left", padx=10)

    ctk.CTkRadioButton(
        target_body,
        text="Dokumente-Verzeichnis verwenden",
        variable=use_documents_var,
        value=True,
    ).pack(anchor="w", padx=6, pady=(4, 6))

    startmenu_card = ctk.CTkFrame(top_row, corner_radius=10, **CARD_STYLE)
    startmenu_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
    ctk.CTkLabel(
        startmenu_card,
        text="Kontextmenü-Modus",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))
    ctk.CTkLabel(
        startmenu_card,
        text="Wählen Sie, welcher Kontextmenü-Modus beim Start des PC-Konfigurators gesetzt werden soll.",
        justify="left",
        wraplength=440,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))
    startmenu_body = ctk.CTkFrame(startmenu_card, fg_color="transparent")
    startmenu_body.pack(fill="x", padx=12, pady=(0, 8))

    ctk.CTkRadioButton(
        startmenu_body,
        text="Windows 11-Kontextmenü bevorzugen (empfohlen)",
        variable=startmenu_mode_var,
        value="win11",
    ).pack(anchor="w", padx=6, pady=2)

    ctk.CTkRadioButton(
        startmenu_body,
        text="Klassisches Kontextmenü dauerhaft aktivieren (Fallback)",
        variable=startmenu_mode_var,
        value="classic",
    ).pack(anchor="w", padx=6, pady=(2, 6))

    hidden_items_card = ctk.CTkFrame(top_row, corner_radius=10, **CARD_STYLE)
    hidden_items_card.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(6, 0))
    ctk.CTkLabel(
        hidden_items_card,
        text="Ausgeblendete Elemente",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))
    ctk.CTkLabel(
        hidden_items_card,
        text="Wählen Sie, ob ausgeblendete Elemente im Explorer standardmäßig angezeigt werden.",
        justify="left",
        wraplength=440,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))
    hidden_items_body = ctk.CTkFrame(hidden_items_card, fg_color="transparent")
    hidden_items_body.pack(fill="x", padx=12, pady=(0, 8))

    ctk.CTkRadioButton(
        hidden_items_body,
        text="standardmäßig ausgeblendet lassen (default)",
        variable=hidden_items_mode_var,
        value="hide",
    ).pack(anchor="w", padx=6, pady=2)

    ctk.CTkRadioButton(
        hidden_items_body,
        text="standardmäßig anzeigen lassen",
        variable=hidden_items_mode_var,
        value="show",
    ).pack(anchor="w", padx=6, pady=(2, 6))

    _font_card, font_body = create_section_card(
        page,
        title="Schriftart-Konfiguration",
        description="Die gewählte Schrift wird in Templates und Office-Einstellungen übernommen.",
    )

    ctk.CTkLabel(
        font_body,
        text=(
            "Hinweis: Classic Outlook übernimmt diese Vorgaben zuverlässig. "
            "Die moderne Outlook-Ansicht kann lokale Standard-Schriftarten/-größen "
            "teilweise ignorieren."
        ),
        font=ctk.CTkFont(size=11),
        text_color="gray",
        wraplength=960,
    ).pack(anchor="w", padx=6, pady=(0, 3))

    selection_row = ctk.CTkFrame(font_body, fg_color="transparent")
    selection_row.pack(fill="x", padx=6, pady=(3, 6))
    selection_row.grid_columnconfigure(0, weight=1)
    selection_row.grid_columnconfigure(1, weight=1)
    selection_row.grid_rowconfigure(0, weight=1)

    font_frame = ctk.CTkFrame(selection_row, **CARD_STYLE)
    font_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=3)

    ctk.CTkLabel(
        font_frame,
        text="Schriftart",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=10, pady=(8, 2))

    ctk.CTkOptionMenu(
        font_frame,
        variable=font_name_var,
        values=available_font_families,
    ).pack(anchor="w", padx=10, pady=(4, 8))

    ctk.CTkButton(
        font_frame,
        text="Font-Vorschau in Fenster öffnen",
        command=on_open_font_preview,
        width=260,
        height=34,
        **PALE_BUTTON_STYLE,
    ).pack(anchor="w", padx=10, pady=(0, 8))

    size_frame = ctk.CTkFrame(selection_row, **CARD_STYLE)
    size_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=3)

    ctk.CTkLabel(
        size_frame,
        text="Schriftgrößen",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=10, pady=(8, 2))

    size_inner = ctk.CTkFrame(size_frame, fg_color="transparent")
    size_inner.pack(fill="x", padx=10, pady=(4, 8))

    ctk.CTkLabel(size_inner, text="Word/Outlook:").pack(anchor="w", padx=2)
    ctk.CTkOptionMenu(size_inner, variable=font_size_word_var, values=["10", "11", "12"]).pack(anchor="w", padx=2, pady=(2, 6))

    ctk.CTkLabel(size_inner, text="Excel:").pack(anchor="w", padx=2)
    ctk.CTkOptionMenu(size_inner, variable=font_size_excel_var, values=["10", "11", "12"]).pack(anchor="w", padx=2, pady=(2, 2))

    com_card = ctk.CTkFrame(page, corner_radius=10, **CARD_STYLE)
    com_card.pack(fill="x", padx=4, pady=(6, 6))

    ctk.CTkLabel(
        com_card,
        text="COM-Synchronisierung (optional)",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))

    ctk.CTkLabel(
        com_card,
        text=(
            "Standardmäßig arbeitet der PC-Konfigurator schnell/stabil über Registry/XML. "
            "Aktivieren Sie COM nur bei Bedarf (z. B. wenn Office auf einzelnen Firmenrechnern "
            "nicht alle Font-Defaults übernimmt)."
        ),
        justify="left",
        wraplength=960,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))

    ctk.CTkCheckBox(
        com_card,
        text="COM-Synchronisierung für Word/Excel aktivieren (langsamer, aber robuster)",
        variable=enable_com_sync_var,
        onvalue=True,
        offvalue=False,
    ).pack(anchor="w", padx=14, pady=(0, 10))

    preclose_card = ctk.CTkFrame(page, corner_radius=10, **CARD_STYLE)
    preclose_card.pack(fill="x", padx=4, pady=(0, 6))

    ctk.CTkLabel(
        preclose_card,
        text="Office vor Konfiguration schließen (empfohlen)",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))

    ctk.CTkLabel(
        preclose_card,
        text=(
            "Beendet Word, Excel und Outlook vor dem Konfigurationslauf. "
            "Das reduziert Datei-Locks und erhöht die Erfolgsquote in Firmenumgebungen."
        ),
        justify="left",
        wraplength=960,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))

    ctk.CTkCheckBox(
        preclose_card,
        text="Office-Anwendungen vor dem Lauf automatisch schließen",
        variable=enable_office_preclose_var,
        onvalue=True,
        offvalue=False,
    ).pack(anchor="w", padx=14, pady=(0, 10))

    warmup_card = ctk.CTkFrame(page, corner_radius=10, **CARD_STYLE)
    warmup_card.pack(fill="x", padx=4, pady=(0, 6))

    ctk.CTkLabel(
        warmup_card,
        text="Office-Warm-up (optional)",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))

    ctk.CTkLabel(
        warmup_card,
        text=(
            "Initialisiert Word und Excel kurz vor dem Lauf. "
            "Hilft bei LTSC-/Profilumgebungen, in denen Defaults sonst erst verzögert greifen."
        ),
        justify="left",
        wraplength=960,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))

    ctk.CTkCheckBox(
        warmup_card,
        text="Word/Excel vor der Konfiguration kurz initialisieren",
        variable=enable_office_warmup_var,
        onvalue=True,
        offvalue=False,
    ).pack(anchor="w", padx=14, pady=(0, 10))

    firm_card = ctk.CTkFrame(page, corner_radius=10, **CARD_STYLE)
    firm_card.pack(fill="x", padx=4, pady=(0, 6))

    ctk.CTkLabel(
        firm_card,
        text="Firmenmodus (robust)",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=CARD_TITLE_COLOR,
    ).pack(anchor="w", padx=14, pady=(10, 3))

    ctk.CTkLabel(
        firm_card,
        text=(
            "Aktiviert eine robuste Voreinstellung für verwaltete Umgebungen: "
            "COM-Sync + Office-Preclose + Office-Warm-up."
        ),
        justify="left",
        wraplength=960,
        text_color=("#4B5563", "#D1D5DB"),
    ).pack(anchor="w", padx=14, pady=(0, 6))

    ctk.CTkCheckBox(
        firm_card,
        text="Firmenmodus aktivieren (empfohlen bei Office LTSC/Firmenrichtlinien)",
        variable=enable_firm_mode_var,
        onvalue=True,
        offvalue=False,
    ).pack(anchor="w", padx=14, pady=(0, 10))

    _next_card, next_body = create_section_card(
        page,
        title="Nächster Schritt",
        description=None,
    )

    next_row = ctk.CTkFrame(next_body, fg_color="transparent")
    next_row.pack(fill="x", padx=6, pady=(2, 2))
    next_row.grid_columnconfigure(0, weight=1)
    next_row.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        next_row,
        text="Wenn die Einstellungen passen, wechseln Sie zur Ausführung.",
        justify="left",
        wraplength=420,
        text_color=("#4B5563", "#D1D5DB"),
    ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)

    ctk.CTkButton(
        next_row,
        text="Weiter",
        command=on_continue_to_execution,
        font=ctk.CTkFont(weight="bold"),
        width=220,
        height=38,
        **CONTINUE_BUTTON_STYLE,
    ).grid(row=0, column=1, sticky="e", padx=(10, 0), pady=2)

    return {}
