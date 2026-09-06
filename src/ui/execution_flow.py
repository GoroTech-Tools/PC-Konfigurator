from __future__ import annotations


def run_full_configuration_flow(
    *,
    root_update,
    system_checker,
    install_all_fonts,
    get_office_settings_from_gui,
    office_configurator,
    template_manager,
    safe_office_config,
    get_office_font_name,
    get_font_size_word,
    get_font_size_excel,
    advance_step,
    append_status,
    add_registry_restart_notice,
    finish_progress,
) -> None:
    """Vollständige Konfiguration inkl. Template-/Registry-Schritten."""
    try:
        overall_success = True

        advance_step("1. System-Check...\n")
        root_update()
        system_info = system_checker.get_system_info()
        append_status(f"   Erfolg: {system_info.get('platform', 'System')} erkannt\n")

        advance_step("2. Alle Schriften aus dem Fonts-Ordner installieren...\n")
        root_update()
        font_result = install_all_fonts()
        if font_result.get("success"):
            installed_count = len(font_result.get("installed_fonts", []))
            refreshed_count = len(font_result.get("refreshed_fonts", []))
            skipped_count = len(font_result.get("skipped_fonts", []))
            if installed_count > 0:
                append_status(f"   Erfolg: {installed_count} Schrift-Datei(en) neu im Benutzerprofil installiert\n")
            elif refreshed_count > 0:
                append_status(f"   Erfolg: {refreshed_count} Schrift-Datei(en) im Benutzerprofil neu registriert\n")
            elif skipped_count > 0:
                append_status("   Alle Schriften sind bereits vorhanden – keine neuen Installationen erforderlich.\n")
            else:
                append_status("   Keine Schrift-Dateien im Fonts-Ordner gefunden.\n")
        else:
            append_status(
                f"   Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n"
            )

        advance_step("3. Office-Konfiguration...\n")
        root_update()

        office_settings = get_office_settings_from_gui()

        if office_settings.get("enable_office_preclose"):
            append_status("   ℹ️ Office-Preclose aktiv: Word/Excel/Outlook werden vorab beendet...\n")
            preclose_result = office_configurator.close_office_apps()
            if preclose_result.get("success"):
                append_status("   ✅ Office-Prozesse wurden vorab verarbeitet\n")
            else:
                append_status(f"   ⚠️ Office-Preclose mit Hinweis: {preclose_result.get('warning', 'Unbekannt')}\n")

        if office_settings.get("enable_office_warmup"):
            append_status("   ℹ️ Office-Warm-up aktiv: Word/Excel werden kurz initialisiert...\n")
            warmup_result = office_configurator.warmup_office_apps()
            if warmup_result.get("success"):
                append_status("   ✅ Office-Warm-up erfolgreich\n")
            else:
                append_status(f"   ⚠️ Office-Warm-up mit Hinweis: {warmup_result.get('warning', 'Unbekannt')}\n")

        result = office_configurator.configure_all_settings(office_settings)

        if result["success"]:
            applied_count = result.get("applied_count")
            if isinstance(applied_count, int):
                append_status(f"   Erfolg: {applied_count} Einstellungen angewendet\n")
            else:
                append_status("   Erfolg: Office-Einstellungen angewendet\n")
            if result.get("word_start_screen_disabled"):
                append_status("   ✅ Word-Startbildschirm deaktiviert (Start mit leerem Dokument)\n")
            if result.get("com_precheck_skipped"):
                append_status("   ℹ️ COM optional nicht verfügbar (Registry/Template aktiv)\n")
            elif result.get("com_sync_ok", True):
                append_status("   ✅ COM: [COM-HEALTH] OK | Word/Excel via COM, Outlook via Registry/MailSettings\n")
            elif result.get("com_sync_warning"):
                append_status(f"   ⚠️ COM: [COM-HEALTH] DEGRADED | {result['com_sync_warning']}\n")
            if result.get("outlook_warning"):
                append_status(f"   ⚠️ Outlook-Template-Schritt: {result['outlook_warning']}\n")
            else:
                append_status("   ✅ Outlook-Template-Schritt: Kopie und Synchronisation abgeschlossen\n")
            if result.get("outlook_modern_notice"):
                append_status(f"   ℹ️ Outlook modern: {result['outlook_modern_notice']}\n")
            if result.get("hidden_items_mode_label"):
                append_status(
                    f"   ℹ️ Ausgeblendete Elemente: {result['hidden_items_mode_label']}\n"
                )
            if result.get("windows_warning"):
                append_status(f"   ⚠️ Windows-Einstellungen: {result['windows_warning']}\n")
        else:
            append_status(f"   Fehler: {result.get('error', 'Unbekannter Fehler')}\n")
            overall_success = False

        advance_step("4. Office-Templates anpassen und kopieren...\n")
        root_update()

        try:
            font_name = get_office_font_name()
            size_word = get_font_size_word()
            size_excel = get_font_size_excel()

            template_names = {
                "normal_dotm": "Word Standard-Template (Normal.dotm)",
                "mappe_xltx": "Excel Standard-Template (Mappe.xltx)",
                "book_xltx": "Excel Zusatz-Template (book.xltx)",
                "normal_email_dotm": "Outlook E-Mail-Template (NormalEmail.dotm)",
            }

            mod_results = template_manager.update_font_in_templates(
                font_name=font_name,
                font_size_word=size_word,
                font_size_excel=size_excel,
                corporate_design=office_settings.get("corporate_design", "INN-tegrativ"),
            )
            copy_results = template_manager.copy_templates_to_user()

            mod_ok = bool(mod_results) and all(bool(v) for v in mod_results.values())
            copy_ok = bool(copy_results) and all(bool(v) for v in copy_results.values())
            # Registry wurde bereits in Schritt 3 über OfficeConfigurator gesetzt.
            registry_ok = True

            failed_mod_templates = [
                template_names.get(key, key)
                for key, ok in mod_results.items()
                if not ok
            ]
            failed_copy_templates = [
                template_names.get(key, key)
                for key, ok in copy_results.items()
                if not ok
            ]

            if mod_ok and copy_ok:
                append_status("   ✅ Templates angepasst und ins Benutzerprofil kopiert\n")
            else:
                append_status("   ❌ Template-Anpassung/Kopie fehlgeschlagen (Details unten)\n")
                if failed_mod_templates:
                    append_status("   ❌ Schrift-/Style-Anpassung fehlgeschlagen für:\n")
                    for name in failed_mod_templates:
                        append_status(f"      - {name}\n")
                if failed_copy_templates:
                    append_status("   ❌ Kopieren ins Benutzerprofil fehlgeschlagen für:\n")
                    for name in failed_copy_templates:
                        append_status(f"      - {name}\n")
                append_status(
                    "   💡 Hinweise: Office-Programme schließen, Schreibrechte in %APPDATA% prüfen und ggf. COM-Synchronisierung in den Einstellungen aktivieren.\n"
                )
                overall_success = False

            verify_result = template_manager.verify_user_template_fonts(
                font_name=font_name,
                font_size_word=size_word,
                font_size_excel=size_excel,
            )

            verify_details = verify_result.get("details", {})
            if verify_result.get("success"):
                append_status("   ✅ Post-Verify: Ziel-Templates im Benutzerprofil entsprechen den erwarteten Font-Defaults\n")
            else:
                append_status("   ❌ Post-Verify: Abweichungen in Ziel-Templates erkannt\n")
                template_names = {
                    "normal_dotm": "Word Standard-Template (Normal.dotm)",
                    "mappe_xltx": "Excel Standard-Template (Mappe.xltx)",
                    "book_xltx": "Excel Zusatz-Template (book.xltx)",
                    "normal_email_dotm": "Outlook E-Mail-Template (NormalEmail.dotm)",
                }
                for key, item in verify_details.items():
                    display_name = template_names.get(key, key)
                    if item.get("ok"):
                        continue
                    reason = item.get("reason") or "Abweichung"
                    actual = item.get("actual") or {}
                    actual_name = actual.get("font_name", "?") if isinstance(actual, dict) else "?"
                    actual_size = actual.get("font_size", "?") if isinstance(actual, dict) else "?"
                    append_status(
                        f"      - {display_name}: {reason} (Ist: {actual_name} {actual_size}pt)\n"
                    )
                overall_success = False

            if registry_ok:
                append_status(f"   ✅ Schriftart konfiguriert: {font_name}\n")
                append_status(f"   ✅ Word/Outlook: {size_word}pt, Excel: {size_excel}pt\n")
                append_status("   ℹ️ Registry-Schriftart wurde bereits in Schritt 3 gesetzt (kein Doppel-Lauf)\n")
            else:
                append_status("   ⚠️ Registry-Schriftart-Konfiguration teilweise fehlgeschlagen\n")
                overall_success = False

        except Exception as template_error:
            append_status(f"   ❌ Template-Fehler: {template_error}\n")
            overall_success = False

        advance_step("5. Abschluss...\n")
        append_status("\nKonfiguration abgeschlossen!\n")
        add_registry_restart_notice()
        finish_progress(success=overall_success)

    except Exception as exc:
        append_status(f"\nFEHLER: {exc}\n")
        finish_progress(success=False)

    root_update()


def run_office_configuration_flow(
    *,
    root_update,
    install_all_fonts,
    get_office_settings_from_gui,
    office_configurator,
    advance_step,
    append_status,
    add_registry_restart_notice,
    finish_progress,
) -> None:
    """Office-only-Ausführung (ohne Windows-Teilkonfiguration)."""
    try:
        advance_step("1. Schriften installieren...\n")
        append_status("Office-Konfiguration startet...\n")
        font_result = install_all_fonts()
        if font_result.get("success"):
            installed_count = len(font_result.get("installed_fonts", []))
            refreshed_count = len(font_result.get("refreshed_fonts", []))
            if installed_count > 0:
                append_status(f"Alle Schriften installiert: {installed_count} Dateien im Benutzerprofil\n")
            elif refreshed_count > 0:
                append_status(f"Alle Schriften neu registriert: {refreshed_count} Dateien im Benutzerprofil\n")
            else:
                append_status("Keine neuen Schrift-Dateien gefunden.\n")
        else:
            append_status(
                f"Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n"
            )
        root_update()

        advance_step("2. Office konfigurieren...\n")
        office_settings = get_office_settings_from_gui()
        result = office_configurator.configure_all_settings(office_settings, include_windows=False)

        if result["success"]:
            applied_count = result.get("applied_count")
            if isinstance(applied_count, int):
                append_status(f"Erfolg: {applied_count} Einstellungen angewendet\n")
            else:
                append_status("Erfolg: Office-Einstellungen angewendet\n")
            if result.get("word_start_screen_disabled"):
                append_status("✅ Word-Startbildschirm deaktiviert (Start mit leerem Dokument)\n")
            if result.get("com_precheck_skipped"):
                append_status("ℹ️ COM optional nicht verfügbar (Registry/Template aktiv)\n")
            elif result.get("com_sync_ok", True):
                append_status("✅ COM: [COM-HEALTH] OK | Word/Excel via COM, Outlook via Registry/MailSettings\n")
            elif result.get("com_sync_warning"):
                append_status(f"⚠️ COM: [COM-HEALTH] DEGRADED | {result['com_sync_warning']}\n")
            if result.get("outlook_warning"):
                append_status(f"⚠️ Outlook-Template-Schritt: {result['outlook_warning']}\n")
            else:
                append_status("✅ Outlook-Template-Schritt: Kopie und Synchronisation abgeschlossen\n")
            if result.get("outlook_modern_notice"):
                append_status(f"ℹ️ Outlook modern: {result['outlook_modern_notice']}\n")
            advance_step("3. Abschluss...\n")
            append_status("Office-Konfiguration abgeschlossen!\n")
            add_registry_restart_notice()
            finish_progress(success=True)
        else:
            append_status(f"Fehler: {result.get('error', 'Unbekannter Fehler')}\n")
            finish_progress(success=False)

    except Exception as exc:
        append_status(f"FEHLER: {exc}\n")
        finish_progress(success=False)

    root_update()
