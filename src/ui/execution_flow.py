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
            append_status(f"   Erfolg: {installed_count} Schrift-Dateien im Benutzerprofil installiert\n")
        else:
            append_status(
                f"   Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n"
            )

        advance_step("3. Office-Konfiguration...\n")
        root_update()

        office_settings = get_office_settings_from_gui()
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
                append_status("   ✅ COM: [COM-HEALTH] OK | Word, Excel, Outlook via COM synchronisiert\n")
            elif result.get("com_sync_warning"):
                append_status(f"   ⚠️ COM: [COM-HEALTH] DEGRADED | {result['com_sync_warning']}\n")
            if result.get("outlook_warning"):
                append_status(f"   ⚠️ Outlook-Template-Schritt: {result['outlook_warning']}\n")
            else:
                append_status("   ✅ Outlook-Template-Schritt: Kopie und Synchronisation abgeschlossen\n")
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

            mod_results = template_manager.update_font_in_templates(
                font_name=font_name,
                font_size_word=size_word,
                font_size_excel=size_excel,
            )
            copy_results = template_manager.copy_templates_to_user()
            safe_results = safe_office_config.configure_fonts_via_registry(
                font_name=font_name,
                font_size_word=size_word,
                font_size_excel=size_excel,
            )

            mod_ok = bool(mod_results) and all(bool(v) for v in mod_results.values())
            copy_ok = bool(copy_results) and all(bool(v) for v in copy_results.values())
            registry_ok = all(bool(v) for k, v in safe_results.items() if k != "error")

            if mod_ok and copy_ok:
                append_status("   ✅ Templates angepasst und ins Benutzerprofil kopiert\n")
            else:
                append_status("   ⚠️ Template-Anpassung/Kopie teilweise fehlgeschlagen (Details im Log)\n")

            if registry_ok:
                append_status(f"   ✅ Schriftart konfiguriert: {font_name}\n")
                append_status(f"   ✅ Word: {size_word}pt, Excel: {size_excel}pt\n")
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
            append_status(f"Alle Schriften installiert: {installed_count} Dateien im Benutzerprofil\n")
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
                append_status("✅ COM: [COM-HEALTH] OK | Word, Excel, Outlook via COM synchronisiert\n")
            elif result.get("com_sync_warning"):
                append_status(f"⚠️ COM: [COM-HEALTH] DEGRADED | {result['com_sync_warning']}\n")
            if result.get("outlook_warning"):
                append_status(f"⚠️ Outlook-Template-Schritt: {result['outlook_warning']}\n")
            else:
                append_status("✅ Outlook-Template-Schritt: Kopie und Synchronisation abgeschlossen\n")
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
