from __future__ import annotations

import customtkinter as ctk

TEMPLATE_NAMES = {
    "normal_dotm": "Word Standard-Template (Normal.dotm)",
    "mappe_xltx": "Excel Standard-Template (Mappe.xltx)",
    "normal_email_dotm": "Outlook E-Mail-Template (NormalEmail.dotm)",
}


def clear_template_status_frame(frame) -> None:
    for widget in frame.winfo_children():
        widget.destroy()


def render_safe_template_status(frame, status: dict) -> None:
    clear_template_status_frame(frame)

    status_info = "Template-Status (Sicherheitscheck):\\n\\n"
    for template_key, template_name in TEMPLATE_NAMES.items():
        template_status = status.get(template_key, "Unbekannt")

        if template_status == "OK":
            status_emoji = "✅"
        elif "Beschädigt" in template_status:
            status_emoji = "⚠️"
        elif "Nicht vorhanden" in template_status:
            status_emoji = "❌"
        else:
            status_emoji = "⚠️"

        status_info += f"{status_emoji} {template_name}\\n"
        status_info += f"   Status: {template_status}\\n\\n"

    status_label = ctk.CTkLabel(
        frame,
        text=status_info,
        justify="left",
        font=ctk.CTkFont(family="Courier New", size=11),
    )
    status_label.pack(anchor="w", padx=10, pady=5)


def render_template_status(frame, status: dict, current_fonts: dict) -> None:
    clear_template_status_frame(frame)

    status_info = "Template-Status:\n\n"

    word_outlook_font = current_fonts.get("normal_email_dotm") or current_fonts.get("normal_dotm") or "Unbekannt"
    excel_font = current_fonts.get("mappe_xltx") or "Unbekannt"
    status_info += f"Word/Outlook: {word_outlook_font}\n"
    status_info += f"Excel: {excel_font}\n\n"

    for template_key, template_name in TEMPLATE_NAMES.items():
        exists = bool(status.get(template_key, False))
        current_font = current_fonts.get(template_key, "Unbekannt")

        status_emoji = "✅" if exists else "❌"
        status_info += f"{status_emoji} {template_name}\n"
        status_info += f"   Aktuell: {current_font}\n\n"

    status_label = ctk.CTkLabel(
        frame,
        text=status_info,
        justify="left",
        font=ctk.CTkFont(family="Courier New", size=11),
    )
    status_label.pack(anchor="w", padx=10, pady=5)


def render_template_status_error(frame, message: str) -> None:
    clear_template_status_frame(frame)
    error_label = ctk.CTkLabel(
        frame,
        text=message,
        text_color="red",
    )
    error_label.pack(anchor="w", padx=10, pady=5)
