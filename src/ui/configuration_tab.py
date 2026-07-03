from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk
import tkinter.font as tkfont

from ui.theme import create_scrollable_page, create_section_card


def build_configuration_tab(
    tabview,
    *,
    use_documents_var,
    target_drive_var,
    startmenu_mode_var,
    font_name_var,
    font_size_word_var,
    font_size_excel_var,
    available_font_families: list[str],
    on_continue_to_execution: Callable[[], None],
) -> dict[str, Any]:
    """Erzeugt den Konfiguration-Tab und gibt benötigte Widget-Referenzen zurück."""
    config_frame = tabview.tab("Konfiguration")

    page = create_scrollable_page(config_frame)

    ctk.CTkLabel(
        page,
        text="Einstellungen",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(anchor="w", padx=8, pady=(2, 10))

    _info_card, info_body = create_section_card(
        page,
        title="Konfigurationshinweise",
        description="Passen Sie die Einstellungen nach Ihren Bedürfnissen an. Alle Änderungen werden im Benutzerkontext gespeichert.",
    )
    ctk.CTkLabel(
        info_body,
        text="Empfehlung: Erst Zielablage und Schriftart prüfen, dann den Lauf starten.",
        wraplength=960,
        justify="left",
    ).pack(anchor="w", padx=4, pady=(0, 4))

    _target_card, target_body = create_section_card(
        page,
        title="Zielverzeichnis für Datei-Vorlagen",
        description="Wählen Sie, wo Office-Vorlagen gespeichert werden sollen.",
    )

    ctk.CTkRadioButton(
        target_body,
        text="Laufwerk verwenden:",
        variable=use_documents_var,
        value=False,
    ).pack(anchor="w", padx=6, pady=2)

    drive_frame = ctk.CTkFrame(target_body)
    drive_frame.pack(fill="x", padx=6, pady=(5, 10))

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
    ).pack(anchor="w", padx=6, pady=(5, 10))

    _startmenu_card, startmenu_body = create_section_card(
        page,
        title="Startmenü-Modus",
        description="Wählen Sie, welcher Modus beim Start des PC-Konfigurators gesetzt werden soll.",
    )

    ctk.CTkRadioButton(
        startmenu_body,
        text="Windows-11-Startmenü bevorzugen (empfohlen)",
        variable=startmenu_mode_var,
        value="win11",
    ).pack(anchor="w", padx=6, pady=2)

    ctk.CTkRadioButton(
        startmenu_body,
        text="Klassisches Startmenü dauerhaft aktivieren (Fallback)",
        variable=startmenu_mode_var,
        value="classic",
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
    ).pack(anchor="w", padx=6, pady=(0, 5))

    selection_row = ctk.CTkFrame(font_body)
    selection_row.pack(fill="x", padx=6, pady=(5, 10))

    font_frame = ctk.CTkFrame(selection_row)
    font_frame.pack(side="left", fill="both", expand=True, padx=(0, 6), pady=5)

    ctk.CTkLabel(font_frame, text="Schriftart:").pack(anchor="w", padx=8, pady=(6, 0))

    ctk.CTkOptionMenu(
        font_frame,
        variable=font_name_var,
        values=available_font_families,
    ).pack(anchor="w", padx=8, pady=(4, 8))

    size_frame = ctk.CTkFrame(selection_row)
    size_frame.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=5)

    size_inner = ctk.CTkFrame(size_frame)
    size_inner.pack(fill="x", padx=8, pady=(8, 8))

    word_size_frame = ctk.CTkFrame(size_inner)
    word_size_frame.pack(side="left", fill="x", expand=True, padx=(0, 4), pady=2)

    ctk.CTkLabel(word_size_frame, text="Schriftgröße Word/Outlook:").pack(anchor="w", padx=5)
    ctk.CTkOptionMenu(word_size_frame, variable=font_size_word_var, values=["10", "11", "12"]).pack(anchor="w", padx=5, pady=5)

    excel_size_frame = ctk.CTkFrame(size_inner)
    excel_size_frame.pack(side="left", fill="x", expand=True, padx=(4, 0), pady=2)

    ctk.CTkLabel(excel_size_frame, text="Schriftgröße Excel:").pack(anchor="w", padx=5)
    ctk.CTkOptionMenu(excel_size_frame, variable=font_size_excel_var, values=["10", "11", "12"]).pack(anchor="w", padx=5, pady=5)

    preview_label = ctk.CTkLabel(
        font_body,
        text="",
        justify="left",
        font=ctk.CTkFont(size=11),
        text_color="gray",
    )
    preview_label.pack(anchor="w", padx=6, pady=(0, 4))

    preview_sample_label = ctk.CTkLabel(
        font_body,
        text="Aa Bb Cc 12345 – Das ist eine Vorschau.",
        justify="left",
        font=ctk.CTkFont(size=16, weight="normal"),
    )
    preview_sample_label.pack(anchor="w", padx=6, pady=(2, 8))

    preview_availability_label = ctk.CTkLabel(
        font_body,
        text="",
        justify="left",
        font=ctk.CTkFont(size=11),
        text_color="gray",
    )
    preview_availability_label.pack(anchor="w", padx=6, pady=(0, 8))

    ctk.CTkLabel(
        font_body,
        text="Fontliste (Vorschau je Schriftart):",
        font=ctk.CTkFont(size=12, weight="bold"),
    ).pack(anchor="w", padx=6, pady=(2, 4))

    font_list_frame = ctk.CTkScrollableFrame(font_body, height=170)
    font_list_frame.pack(fill="x", padx=6, pady=(0, 6))

    font_preview_rows: dict[str, ctk.CTkLabel] = {}
    default_preview_font = ctk.CTkFont(size=13)

    for family_name in available_font_families:
        row = ctk.CTkLabel(
            font_list_frame,
            text=family_name,
            anchor="w",
            justify="left",
            font=ctk.CTkFont(family=family_name, size=13),
        )
        row.pack(fill="x", padx=6, pady=2)
        font_preview_rows[family_name] = row

    def _font_available(font_family: str) -> bool:
        try:
            available = {name.lower() for name in tkfont.families()}
            return font_family.lower() in available
        except Exception:
            return False

    def _refresh_font_list_preview() -> None:
        for family_name, row in font_preview_rows.items():
            is_available = _font_available(family_name)
            try:
                row.configure(
                    text=f"{family_name}{'' if is_available else ' (nicht lokal verfügbar)'}",
                    font=ctk.CTkFont(family=family_name, size=13) if is_available else default_preview_font,
                    text_color=("#111827", "#E5E7EB") if is_available else ("#6B7280", "#9CA3AF"),
                )
            except Exception:
                row.configure(
                    text=f"{family_name} (Vorschau nicht verfügbar)",
                    font=default_preview_font,
                    text_color=("#6B7280", "#9CA3AF"),
                )

    def _update_font_preview(*_args):
        try:
            selected_font = str(font_name_var.get()).strip()
            word_size = str(font_size_word_var.get()).strip()
            excel_size = str(font_size_excel_var.get()).strip()
            is_available = _font_available(selected_font)
            preview_label.configure(
                text=(
                    "Aktuelle Auswahl:\n"
                    f"Word/Outlook: {selected_font} {word_size} pt\n"
                    f"Excel: {selected_font} {excel_size} pt"
                )
            )
            preview_sample_label.configure(
                text=f"Aa Bb Cc 12345 – {selected_font} in {word_size} pt",
                font=ctk.CTkFont(family=selected_font, size=int(word_size)) if is_available else ctk.CTkFont(size=int(word_size)),
                text_color=("#111827", "#E5E7EB") if is_available else ("#6B7280", "#9CA3AF"),
            )
            preview_availability_label.configure(
                text=(
                    "Schriftart ist lokal verfügbar."
                    if is_available
                    else "Schriftart aktuell nicht lokal verfügbar (wird ggf. durch den Konfigurator bereitgestellt)."
                ),
                text_color=("#1F7A3D", "#8EE6A9") if is_available else ("#8A4B00", "#FFC37A"),
            )
            _refresh_font_list_preview()
        except Exception:
            preview_label.configure(text="Aktuelle Auswahl: (nicht verfügbar)")
            preview_sample_label.configure(
                text="Aa Bb Cc 12345 – Vorschau nicht verfügbar",
                font=ctk.CTkFont(size=14),
                text_color=("#6B7280", "#9CA3AF"),
            )
            preview_availability_label.configure(text="Schriftprüfung derzeit nicht verfügbar.")

    for var in (font_name_var, font_size_word_var, font_size_excel_var):
        try:
            var.trace_add("write", _update_font_preview)
        except Exception:
            pass

    _update_font_preview()

    _next_card, next_body = create_section_card(
        page,
        title="Nächster Schritt",
        description="Wenn die Einstellungen passen, wechseln Sie zur Ausführung.",
    )
    ctk.CTkButton(
        next_body,
        text="Weiter",
        command=on_continue_to_execution,
        font=ctk.CTkFont(weight="bold"),
        height=38,
    ).pack(anchor="e", padx=6, pady=(2, 2))

    return {}
