from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk


def run_safe_restore_templates_dialog(
    root,
    *,
    font_name_display: str,
    font_size_word: int,
    font_size_excel: int,
    office_font_name: str,
    install_all_fonts,
    safe_office_config,
    on_refresh_status,
) -> None:
    """Sichere Template-Wiederherstellung inkl. Registry-Font-Setup."""
    try:
        result = messagebox.askyesno(
            "Sichere Template-Wiederherstellung",
            "SICHERE TEMPLATE-WIEDERHERSTELLUNG\n\n"
            "Was passiert:\n"
            "✅ Beschädigte Templates werden durch Original-Versionen ersetzt\n"
            "✅ Schriftart-Einstellungen werden über Registry gesetzt (sicher!)\n"
            "✅ Keine direkte Template-Manipulation\n\n"
            f"Gewählte Schriftart: {font_name_display}\n"
            f"Word/Outlook-Größe: {font_size_word}pt\n"
            f"Excel-Größe: {font_size_excel}pt\n\n"
            "Fortfahren?",
            icon="question",
        )

        if not result:
            return

        progress_window = ctk.CTkToplevel(root)
        progress_window.title("Sichere Template-Wiederherstellung...")
        progress_window.geometry("450x150")
        progress_window.transient(root)
        progress_window.grab_set()

        progress_label = ctk.CTkLabel(progress_window, text="Templates werden sicher wiederhergestellt...")
        progress_label.pack(pady=20)

        progress_details = ctk.CTkLabel(progress_window, text="", justify="left")
        progress_details.pack(pady=10)

        progress_details.configure(text="Sichere Schriftart-Konfiguration...")
        progress_window.update()

        font_install_result = install_all_fonts()

        results = safe_office_config.safe_font_setup(
            font_name=office_font_name,
            font_size_word=font_size_word,
            font_size_excel=font_size_excel,
        )

        progress_window.destroy()

        if results["success"]:
            recovered_templates = sum(results["template_recovery"].values())
            total_templates = len(results["template_recovery"])
            installed_font_count = len(font_install_result.get("installed_fonts", []))

            messagebox.showinfo(
                "✅ Sichere Wiederherstellung erfolgreich!",
                f"Templates und Schriftarten erfolgreich konfiguriert!\n\n"
                f"📁 Templates wiederhergestellt: {recovered_templates}/{total_templates}\n"
                f"📝 Schriftart-Konfiguration: Erfolgreich\n"
                f"🔤 Installierte Font-Dateien: {installed_font_count}\n\n"
                f"🎯 Neue Einstellungen:\n"
                f"• Schriftart: {font_name_display}\n"
                f"• Word/Outlook: {font_size_word}pt\n"
                f"• Excel: {font_size_excel}pt\n\n"
                f"➤ Starten Sie Office-Programme neu für beste Ergebnisse!",
            )
        else:
            messagebox.showwarning(
                "⚠️ Teilweise erfolgreich",
                f"Wiederherstellung teilweise erfolgreich.\n\n"
                f"Template-Wiederherstellung: {results['template_recovery']}\n"
                f"Font-Konfiguration: {results['font_configuration']}\n\n"
                f"Überprüfen Sie die Log-Dateien für Details.",
            )

        on_refresh_status()
    except Exception as exc:
        messagebox.showerror("Fehler", f"Fehler bei sicherer Template-Wiederherstellung: {str(exc)}")


def run_update_office_templates_dialog(
    root,
    *,
    font_name_display: str,
    font_size_word: int,
    font_size_excel: int,
    template_manager,
    on_refresh_status,
) -> None:
    """Kopiert und aktualisiert Office-Templates mit Benutzerdialogen."""
    try:
        office_warning = messagebox.askyesno(
            "Office-Programme schließen",
            "WICHTIG: Für beste Ergebnisse sollten alle Office-Programme geschlossen sein.\n\n"
            "Sind Word, Excel und Outlook geschlossen?\n\n"
            "➤ JA: Fortfahren mit Template-Update\n"
            "➤ NEIN: Zuerst Office-Programme schließen",
            icon="question",
        )

        if not office_warning:
            messagebox.showinfo(
                "Template-Update abgebrochen",
                "Bitte schließen Sie alle Office-Programme und versuchen Sie es erneut.\n\n"
                "Office-Programme:\n• Microsoft Word\n• Microsoft Excel\n• Microsoft Outlook\n• Microsoft PowerPoint",
            )
            return

        result = messagebox.askyesno(
            "Templates aktualisieren",
            "Möchten Sie die Office-Templates kopieren und mit der gewählten Schriftart aktualisieren?\n\n"
            f"Gewählte Schriftart: {font_name_display}\n\n"
            "Was passiert:\n"
            "• Normal.dotm → Word Standard-Template\n"
            "• Mappe.xltx → Excel Standard-Template\n"
            "• NormalEmail.dotm → Outlook E-Mail-Template\n\n"
            "Bestehende Templates werden überschrieben!",
        )

        if not result:
            return

        progress_window = ctk.CTkToplevel(root)
        progress_window.title("Templates werden aktualisiert...")
        progress_window.geometry("400x200")
        progress_window.transient(root)
        progress_window.grab_set()

        progress_label = ctk.CTkLabel(progress_window, text="Templates werden kopiert und aktualisiert...")
        progress_label.pack(pady=20)

        progress_details = ctk.CTkLabel(progress_window, text="", justify="left")
        progress_details.pack(pady=10)

        progress_details.configure(text="Schritt 1/2: Templates kopieren...")
        progress_window.update()

        progress_details.configure(text="Schritt 1/2: Schriftarten aktualisieren...")
        progress_window.update()

        font_results = template_manager.update_font_in_templates(
            font_name=font_name_display,
            font_size_word=font_size_word,
            font_size_excel=font_size_excel,
        )

        progress_details.configure(text="Schritt 2/2: Templates kopieren...")
        progress_window.update()

        copy_results = template_manager.copy_templates_to_user()

        progress_window.destroy()

        success_count = sum(copy_results.values()) + sum(font_results.values())
        total_operations = len(copy_results) + len(font_results)

        failed_templates = []
        successful_templates = []

        for template_key in copy_results.keys():
            copy_ok = copy_results[template_key]
            font_ok = font_results[template_key]

            template_names = {
                "normal_dotm": "Word Standard-Template",
                "mappe_xltx": "Excel Standard-Template",
                "normal_email_dotm": "Outlook E-Mail-Template",
            }

            template_name = template_names.get(template_key, template_key)

            if copy_ok and font_ok:
                successful_templates.append(f"✅ {template_name}")
            elif copy_ok and not font_ok:
                failed_templates.append(f"⚠️ {template_name} (kopiert, aber Schriftart-Update fehlgeschlagen)")
            elif not copy_ok and font_ok:
                failed_templates.append(f"⚠️ {template_name} (Schriftart aktualisiert, aber Kopieren fehlgeschlagen)")
            else:
                failed_templates.append(f"❌ {template_name} (komplett fehlgeschlagen)")

        if success_count == total_operations:
            messagebox.showinfo(
                "✅ Vollständig erfolgreich!",
                f"Alle Templates erfolgreich aktualisiert!\n\n"
                f"Erfolgreiche Templates:\n"
                + "\n".join(successful_templates)
                + f"\n\nNeue Standard-Schriftart: {font_name_display}\n"
                f"Word/Outlook-Größe: {font_size_word}pt, Excel-Größe: {font_size_excel}pt\n\n"
                f"➤ Neue Word-Dokumente verwenden jetzt {font_name_display}!\n"
                f"➤ Neue Excel-Dokumente verwenden jetzt {font_name_display}!\n"
                f"➤ Neue E-Mails verwenden jetzt {font_name_display}!",
            )
        elif len(successful_templates) > 0:
            message = "Templates teilweise aktualisiert:\n\n"

            if successful_templates:
                message += "Erfolgreich:\n" + "\n".join(successful_templates) + "\n\n"

            if failed_templates:
                message += "Probleme:\n" + "\n".join(failed_templates) + "\n\n"

            message += "Mögliche Ursachen für Probleme:\n"
            message += "• Office-Programme (Word/Excel/Outlook) sind noch geöffnet\n"
            message += "• Template-Dateien werden von anderen Programmen verwendet\n\n"
            message += "Empfehlung: Alle Office-Programme schließen und erneut versuchen."

            messagebox.showwarning("⚠️ Teilweise erfolgreich", message)
        else:
            messagebox.showerror(
                "❌ Fehler bei Template-Update",
                "Leider konnten keine Templates aktualisiert werden.\n\n"
                "Mögliche Ursachen:\n"
                "• Office-Programme sind geöffnet (Word, Excel, Outlook)\n"
                "• Template-Dateien sind gesperrt\n"
                "• Keine Berechtigung für Template-Verzeichnisse\n\n"
                "Lösungsvorschläge:\n"
                "1. Alle Office-Programme schließen\n"
                "2. Als Administrator ausführen\n"
                "3. Überprüfen Sie die Log-Dateien für Details",
            )

        on_refresh_status()
    except Exception as exc:
        messagebox.showerror("Fehler", f"Fehler beim Aktualisieren der Templates: {str(exc)}")
