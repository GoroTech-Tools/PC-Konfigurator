from __future__ import annotations


def configure_office_settings_flow(
    *,
    config: dict,
    template_manager,
    safe_office_config,
    office_configurator,
    logger,
    add_status_text,
) -> dict:
    """Führt den hybriden Office-Konfigurationsablauf aus."""
    try:
        font_name = config.get("font_name", "Aptos")
        font_size_word = config.get("font_size_word", 11)
        font_size_outlook = config.get("font_size_outlook", 12)
        font_size_excel = config.get("font_size_excel", 10)
        add_status_text(f"🔧 Konfiguriere Office mit {font_name} (Word: {font_size_word}pt, Outlook: {font_size_outlook}pt, Excel: {font_size_excel}pt)")

        add_status_text("📄 Standards-Templates werden angepasst...")
        mod_success = 0
        mod_total = 0
        copy_success = 0
        copy_total = 0
        modification_phase = {}
        copy_phase = {}
        overall_success = False

        try:
            mod_result = template_manager.update_font_in_templates(
                font_name=font_name,
                font_size_word=font_size_word,
                font_size_outlook=font_size_outlook,
                font_size_excel=font_size_excel,
            )
            modification_phase = {k: {"success": v} for k, v in mod_result.items()}
            mod_success = sum(1 for v in mod_result.values() if v)
            mod_total = len(mod_result)
        except Exception as exc:
            logger.error(f"Fehler bei Template-Anpassung: {exc}")
            add_status_text(f"❌ Fehler bei Template-Anpassung: {exc}")

        add_status_text("📄 Standards-Templates werden kopiert...")
        try:
            copy_result = template_manager.copy_templates_to_user()
            copy_phase = {k: {"success": v} for k, v in copy_result.items()}
            copy_success = sum(1 for v in copy_result.values() if v)
            copy_total = len(copy_result)
        except Exception as exc:
            logger.error(f"Fehler beim Kopieren der Templates: {exc}")
            add_status_text(f"❌ Fehler beim Kopieren der Templates: {exc}")

        if mod_success == mod_total and mod_total > 0:
            add_status_text(f"✅ Alle {mod_total} Standards-Templates angepasst ({font_name})")
        elif mod_success > 0:
            add_status_text(f"⚠️ {mod_success}/{mod_total} Templates angepasst")
        else:
            add_status_text("❌ Template-Anpassung fehlgeschlagen")

        if copy_success == copy_total and copy_total > 0:
            add_status_text(f"✅ Alle {copy_total} Templates in Benutzerverzeichnisse kopiert")
        elif copy_success > 0:
            add_status_text(f"⚠️ {copy_success}/{copy_total} Templates kopiert")
        else:
            add_status_text("❌ Template-Kopierung fehlgeschlagen")

        overall_success = mod_success == mod_total and copy_success == copy_total and mod_total > 0
        template_results = {
            "modification_phase": modification_phase,
            "copy_phase": copy_phase,
            "overall_success": overall_success,
        }

        registry_results = safe_office_config.configure_safe_office_defaults(
            font_name,
            font_size_word,
            font_size_excel,
            font_size_outlook,
        )
        if registry_results["success"]:
            add_status_text("✅ Registry-Konfiguration erfolgreich")
        else:
            add_status_text("⚠️ Registry-Konfiguration teilweise fehlgeschlagen")

        fallback_results = office_configurator.configure_all_settings(config)

        overall_success = (
            template_results.get("overall_success", False)
            or registry_results.get("success", False)
            or fallback_results.get("success", False)
        )

        return {
            "success": overall_success,
            "template_results": template_results,
            "template_success": template_results.get("overall_success", False),
            "registry_results": registry_results,
            "fallback_results": fallback_results,
        }

    except Exception as exc:
        logger.error(f"Fehler bei Office-Konfiguration: {exc}")
        add_status_text(f"❌ Fehler bei Office-Konfiguration: {exc}")
        return {"success": False, "error": str(exc)}
