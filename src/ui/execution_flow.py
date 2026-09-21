from __future__ import annotations


def run_full_configuration_flow(
    *,
    root_update,
    system_checker,
    install_all_fonts,
    get_office_settings_from_gui,
    office_configurator,
    edge_profile_manager,
    template_manager,
    safe_office_config,
    reset_file_templates,
    sync_file_templates,
    get_office_font_name,
    get_font_size_word,
    get_font_size_outlook,
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

        office_settings = get_office_settings_from_gui()

        advance_step("2. Datei-Vorlagen zurücksetzen (falls aktiviert)...\n")
        root_update()
        if office_settings.get("enable_office_preclose"):
            append_status("   ℹ️ Office-Preclose aktiv: Word/Excel/Outlook werden vor der Vorlagen-Synchronisation beendet...\n")
            preclose_result = office_configurator.close_office_apps()
            if preclose_result.get("success"):
                append_status("   ✅ Office-Prozesse wurden vor der Vorlagen-Synchronisation verarbeitet\n")
            else:
                append_status(f"   ⚠️ Office-Preclose mit Hinweis: {preclose_result.get('warning', 'Unbekannt')}\n")

        reset_result = reset_file_templates(office_settings)
        if reset_result.get("performed"):
            if reset_result.get("success"):
                append_status(f"   ✅ Datei-Vorlagen zurückgesetzt: {reset_result.get('message')}\n")
            else:
                append_status(f"   ⚠️ Datei-Vorlagen-Reset fehlgeschlagen: {reset_result.get('error', 'Unbekannter Fehler')}\n")
                overall_success = False
        else:
            append_status("   ℹ️ Datei-Vorlagen-Reset nicht aktiviert (übersprungen)\n")

        advance_step("3. Datei-Vorlagen-Bibliothek synchronisieren...\n")
        root_update()
        sync_result = sync_file_templates(office_settings)
        if sync_result.get("success"):
            append_status(f"   ✅ Datei-Vorlagen synchronisiert: {sync_result.get('message', 'aktuell')}\n")
            building_blocks_sync = sync_result.get("building_blocks", {})
            if building_blocks_sync.get("status") == "restored":
                append_status("   ✅ Neuere Building-Blocks-Sicherung ins Benutzerprofil übernommen\n")
            elif building_blocks_sync.get("status") == "backed_up":
                append_status("   ✅ Persönliche Building Blocks in Datei-Vorlagen\\Sonstiges\\Building Blocks gesichert\n")
            elif building_blocks_sync.get("status") == "error":
                append_status(
                    f"   ⚠️ Persönliches Building-Blocks-Backup konnte nicht aktualisiert werden: "
                    f"{building_blocks_sync.get('error', 'Unbekannter Fehler')}\n"
                )
        else:
            append_status(f"   ⚠️ Datei-Vorlagen-Synchronisation fehlgeschlagen: {sync_result.get('error', 'Unbekannter Fehler')}\n")
            overall_success = False

        advance_step("4. Alle Schriften aus dem Fonts-Ordner installieren...\n")
        root_update()
        font_result = install_all_fonts()
        if font_result.get("success"):
            installed_count = len(font_result.get("installed_fonts", []))
            skipped_count = len(font_result.get("skipped_fonts", []))
            total_count = font_result.get("total_processed", installed_count + skipped_count)
            if total_count > 0:
                append_status(
                    f"   Erfolg: {installed_count} von {total_count} Schrift-Datei(en) neu hinzugefügt"
                    f" ({skipped_count} bereits vorhanden)\n"
                )
            else:
                append_status("   Keine Schrift-Dateien im Fonts-Ordner gefunden.\n")
        else:
            append_status(
                f"   Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n"
            )

        advance_step("5. Edge-Profile und E-Mail-Signaturen wiederherstellen...")
        root_update()
        if office_settings.get("enable_edge_profile_sync"):
            edge_restore = edge_profile_manager.restore(office_settings)
            if edge_restore.get("restored"):
                append_status(f"   ✅ Edge-/Signatur-Backup: {edge_restore.get('message')}\n")
            elif edge_restore.get("signature_backup_available"):
                append_status("   ℹ️ Edge-/Signatur-Backup: Lokale E-Mail-Signaturen waren bereits vorhanden\n")
            else:
                append_status(f"   ℹ️ Edge-/Signatur-Backup: {edge_restore.get('message', 'Kein Backup vorhanden.')}\n")
            if edge_restore.get("success") and edge_restore.get("signature_backup_available") and not edge_restore.get("signatures"):
                append_status("   ℹ️ E-Mail-Signaturen: Vorhandene lokale Signaturen wurden beibehalten\n")
            elif edge_restore.get("success") and not edge_restore.get("signature_backup_available"):
                append_status("   ℹ️ E-Mail-Signaturen: Kein Backup vorhanden oder keine Wiederherstellung erforderlich\n")
            elif not edge_restore.get("success"):
                append_status(f"   ⚠️ Edge-Backup konnte nicht wiederhergestellt werden: {edge_restore.get('error', 'Unbekannter Fehler')}\n")
        else:
            append_status("   ℹ️ Edge-Profile synchronisieren nicht aktiviert (übersprungen)\n")

        advance_step("6. Office-Konfiguration...\n")
        root_update()

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

        advance_step("7. Office-Templates anpassen und kopieren...\n")
        root_update()

        try:
            font_name = get_office_font_name()
            size_word = get_font_size_word()
            size_outlook = get_font_size_outlook()
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
                font_size_outlook=size_outlook,
                font_size_excel=size_excel,
                corporate_design=office_settings.get("corporate_design", "INN-tegrativ"),
            )
            building_blocks_result = mod_results.get("building_blocks", {}) if isinstance(mod_results, dict) else {}
            if isinstance(building_blocks_result, dict) and building_blocks_result:
                found_names = [name for name, ok in building_blocks_result.items() if ok]
                if found_names:
                    append_status(f"   ✅ Building Blocks erkannt und angepasst: {', '.join(found_names)}\n")
                else:
                    append_status("   ℹ️ Building Blocks nicht gefunden; der normale Word-Flow blieb unverändert\n")
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
                font_size_outlook=size_outlook,
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
                    actual_name = actual.get("font_name") or "?" if isinstance(actual, dict) else "?"
                    actual_size = actual.get("font_size") if isinstance(actual, dict) else None
                    actual_size = actual_size if actual_size is not None else "?"
                    append_status(
                        f"      - {display_name}: {reason} (Ist: {actual_name} {actual_size}pt)\n"
                    )
                overall_success = False

            if registry_ok:
                append_status(f"   ✅ Schriftart konfiguriert: {font_name}\n")
                append_status(f"   ✅ Word: {size_word}pt, Outlook: {size_outlook}pt, Excel: {size_excel}pt\n")
                append_status("   ℹ️ Registry-Schriftart wurde bereits in Schritt 3 gesetzt (kein Doppel-Lauf)\n")
            else:
                append_status("   ⚠️ Registry-Schriftart-Konfiguration teilweise fehlgeschlagen\n")
                overall_success = False

        except Exception as template_error:
            append_status(f"   ❌ Template-Fehler: {template_error}\n")
            overall_success = False

        advance_step("8. Edge-Profile und E-Mail-Signaturen sichern/aktualisieren...")
        root_update()
        if office_settings.get("enable_edge_profile_sync"):
            edge_backup = edge_profile_manager.backup(office_settings)
            if edge_backup.get("backed_up"):
                append_status(f"   ✅ Edge-/Signatur-Backup: {edge_backup.get('message')}\n")
                if edge_backup.get("signatures"):
                    append_status("   ✅ E-Mail-Signaturen: Sicherung aktualisiert\n")
                else:
                    append_status("   ℹ️ E-Mail-Signaturen: Keine lokalen Signaturen vorhanden\n")
            else:
                append_status(f"   ℹ️ Edge-/Signatur-Backup: {edge_backup.get('message', 'Keine Daten gefunden.')}\n")
            if not edge_backup.get("success"):
                append_status(f"   ⚠️ Edge-Backup konnte nicht erstellt werden: {edge_backup.get('error', 'Unbekannter Fehler')}\n")
        else:
            append_status("   ℹ️ Edge-Profile synchronisieren nicht aktiviert (übersprungen)\n")

        advance_step("9. Abschluss...\n")
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
    edge_profile_manager,
    reset_file_templates,
    sync_file_templates,
    advance_step,
    append_status,
    add_registry_restart_notice,
    finish_progress,
) -> None:
    """Office-only-Ausführung (ohne Windows-Teilkonfiguration)."""
    try:
        office_settings = get_office_settings_from_gui()

        advance_step("1. Datei-Vorlagen zurücksetzen (falls aktiviert)...\n")
        append_status("Office-Konfiguration startet...\n")
        if office_settings.get("enable_office_preclose"):
            append_status("ℹ️ Office-Preclose aktiv: Word/Excel/Outlook werden vor der Vorlagen-Synchronisation beendet...\n")
            preclose_result = office_configurator.close_office_apps()
            if preclose_result.get("success"):
                append_status("✅ Office-Prozesse wurden vor der Vorlagen-Synchronisation verarbeitet\n")
            else:
                append_status(f"⚠️ Office-Preclose mit Hinweis: {preclose_result.get('warning', 'Unbekannt')}\n")

        reset_result = reset_file_templates(office_settings)
        if reset_result.get("performed"):
            if reset_result.get("success"):
                append_status(f"✅ Datei-Vorlagen zurückgesetzt: {reset_result.get('message')}\n")
            else:
                append_status(f"⚠️ Datei-Vorlagen-Reset fehlgeschlagen: {reset_result.get('error', 'Unbekannter Fehler')}\n")
        else:
            append_status("ℹ️ Datei-Vorlagen-Reset nicht aktiviert (übersprungen)\n")
        root_update()

        advance_step("2. Datei-Vorlagen-Bibliothek synchronisieren...\n")
        sync_result = sync_file_templates(office_settings)
        if sync_result.get("success"):
            append_status(f"✅ Datei-Vorlagen synchronisiert: {sync_result.get('message', 'aktuell')}\n")
            building_blocks_sync = sync_result.get("building_blocks", {})
            if building_blocks_sync.get("status") == "error":
                append_status(
                    f"⚠️ Persönliches Building-Blocks-Backup konnte nicht aktualisiert werden: "
                    f"{building_blocks_sync.get('error', 'Unbekannter Fehler')}\n"
                )
        else:
            append_status(f"⚠️ Datei-Vorlagen-Synchronisation fehlgeschlagen: {sync_result.get('error', 'Unbekannter Fehler')}\n")
        root_update()

        advance_step("3. Schriften installieren...\n")
        font_result = install_all_fonts()
        if font_result.get("success"):
            installed_count = len(font_result.get("installed_fonts", []))
            skipped_count = len(font_result.get("skipped_fonts", []))
            total_count = font_result.get("total_processed", installed_count + skipped_count)
            if total_count > 0:
                append_status(
                    f"{installed_count} von {total_count} Schrift-Datei(en) neu hinzugefügt"
                    f" ({skipped_count} bereits vorhanden)\n"
                )
            else:
                append_status("Keine neuen Schrift-Dateien gefunden.\n")
        else:
            append_status(
                f"Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n"
            )
        root_update()

        advance_step("4. Edge-Profile und E-Mail-Signaturen wiederherstellen...")
        if office_settings.get("enable_edge_profile_sync"):
            edge_restore = edge_profile_manager.restore(office_settings)
            if edge_restore.get("restored"):
                append_status(f"Edge-/Signatur-Backup: {edge_restore.get('message')}\n")
            elif edge_restore.get("signature_backup_available"):
                append_status("ℹ️ E-Mail-Signaturen: Vorhandene lokale Signaturen wurden beibehalten\n")
            else:
                append_status(f"ℹ️ Edge-/Signatur-Backup: {edge_restore.get('message', 'Kein Backup vorhanden.')}\n")
                if edge_restore.get("success"):
                    append_status("ℹ️ E-Mail-Signaturen: Kein Backup vorhanden oder keine Wiederherstellung erforderlich\n")
            if not edge_restore.get("success"):
                append_status(f"⚠️ Edge-Backup konnte nicht wiederhergestellt werden: {edge_restore.get('error', 'Unbekannter Fehler')}\n")
        else:
            append_status("ℹ️ Edge-Profile synchronisieren nicht aktiviert (übersprungen)\n")

        advance_step("5. Office konfigurieren...\n")
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
            advance_step("6. Edge-Profile und E-Mail-Signaturen sichern/aktualisieren...")
            if office_settings.get("enable_edge_profile_sync"):
                edge_backup = edge_profile_manager.backup(office_settings)
                if edge_backup.get("backed_up"):
                    append_status(f"✅ Edge-/Signatur-Backup: {edge_backup.get('message')}\n")
                    if edge_backup.get("signatures"):
                        append_status("✅ E-Mail-Signaturen: Sicherung aktualisiert\n")
                    else:
                        append_status("ℹ️ E-Mail-Signaturen: Keine lokalen Signaturen vorhanden\n")
                else:
                    append_status(f"ℹ️ Edge-/Signatur-Backup: {edge_backup.get('message', 'Keine Daten gefunden.')}\n")
                if not edge_backup.get("success"):
                    append_status(f"⚠️ Edge-Backup konnte nicht erstellt werden: {edge_backup.get('error', 'Unbekannter Fehler')}\n")
            else:
                append_status("ℹ️ Edge-Profile synchronisieren nicht aktiviert (übersprungen)\n")
            if result.get("outlook_modern_notice"):
                append_status(f"ℹ️ Outlook modern: {result['outlook_modern_notice']}\n")
            advance_step("7. Abschluss...\n")
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
