"""
Office-Konfiguration Module
===========================

Konfiguriert Office-Programme (Word, Excel) mit Schriftarten, Pfaden und anderen Einstellungen.
Portiert aus dem ursprünglichen PowerShell-Skript.
Jetzt mit detaillierten Registry-Erläuterungen.
"""

import winreg
import os
import logging
import shutil
import time
import subprocess
import re
from pathlib import Path
from registry_explainer import RegistryExplainer


class OfficeConfigurator:
    """Klasse zur Konfiguration von Office-Programmen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry_explainer = RegistryExplainer()
        self.applied_settings = []  # Track applied settings for logging

    @staticmethod
    def _is_truthy(value) -> bool:
        """Robuste Bool-Auswertung für Config-/Umgebungswerte."""
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

    def _bootstrap_office_com(self, config: dict | None = None) -> dict:
        """Prüft nur die COM-Laufzeit und vermeidet langsame Office-Vorabstarts."""
        result = { 
            "ready": True,
            "skip_com": True,
            "summary": None,
            "details": {},
        }

        # COM-Sync ist standardmäßig deaktiviert (Performance/Stabilität).
        # Priorität: GUI-Config > Umgebungsvariable > Default(False).
        config_value = None if config is None else config.get("enable_com_sync")
        env_value = os.environ.get("PCONFIG_ENABLE_COM_SYNC", "0")
        enable_com_sync = self._is_truthy(config_value) if config_value is not None else self._is_truthy(env_value)

        if not enable_com_sync:
            result["summary"] = "COM-Synchronisierung deaktiviert; Registry/XML-Pfade aktiv."
            result["details"] = {"mode": "registry+xml", "com_sync": "disabled"}
            return result

        try:
            import pythoncom  # type: ignore
            import win32com.client  # type: ignore

            pythoncom.CoInitialize()
            try:
                result["details"] = {
                    "pythoncom": "ok",
                    "win32com": "ok",
                    "mode": "lazy+com",
                }
                result["summary"] = "COM-Laufzeit verfügbar; Word/Excel werden nur bei Bedarf geöffnet. Outlook nutzt primär Registry/MailSettings."
            finally:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        except Exception as exc:
            result["ready"] = False
            result["skip_com"] = True
            result["summary"] = f"COM-Vorabprüfung nicht möglich: {exc}"

        return result

    def _is_new_outlook_installed(self) -> bool:
        """Ermittelt heuristisch, ob das neue Outlook (Monarch/Store-App) vorhanden ist."""
        try:
            candidates = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "olk.exe",
                Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "WindowsApps",
            ]
            return any(p.exists() for p in candidates)
        except Exception:
            return False

    def _get_new_outlook_notice(self) -> str | None:
        """Hinweistext zur Einschränkung von Schriftdefaults im neuen Outlook."""
        if not self._is_new_outlook_installed():
            return None
        return (
            "Neues Outlook erkannt: Die moderne Ansicht übernimmt lokale Standard-"
            "Schriftarten/-größen aus Registry/NormalEmail.dotm nur eingeschränkt. "
            "Classic Outlook wird vollständig unterstützt."
        )

    def close_office_apps(self) -> dict:
        """Beendet Word, Excel und Outlook vor dem Konfigurationslauf."""
        process_names = ["WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE"]
        warnings: list[str] = []

        for proc in process_names:
            try:
                result = subprocess.run(
                    ["taskkill", "/IM", proc, "/F"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode in (0, 128):
                    # 128 = Prozess nicht gefunden (kein Fehler für unseren Use-Case)
                    self.logger.info(f"Office-Preclose verarbeitet: {proc}")
                else:
                    stderr = (result.stderr or "").strip()
                    warnings.append(f"{proc}: {stderr or 'taskkill return code ' + str(result.returncode)}")
            except Exception as exc:
                warnings.append(f"{proc}: {exc}")

        if warnings:
            message = "Office-Preclose mit Warnungen: " + "; ".join(warnings)
            self.logger.warning(message)
            return {"success": False, "warning": message}

        return {"success": True, "message": "Office-Anwendungen wurden verarbeitet."}

    def warmup_office_apps(self) -> dict:
        """Initialisiert Word/Excel kurz per COM und beendet die Instanzen wieder."""
        warnings: list[str] = []
        apps = [
            ("Word", "Word.Application"),
            ("Excel", "Excel.Application"),
        ]

        try:
            import pythoncom  # type: ignore
            import win32com.client  # type: ignore
        except Exception as exc:
            message = f"Office-Warm-up nicht verfügbar (COM fehlt): {exc}"
            self.logger.warning(message)
            return {"success": False, "warning": message}

        try:
            pythoncom.CoInitialize()
        except Exception:
            pass

        try:
            for label, prog_id in apps:
                app = None
                try:
                    app = win32com.client.DispatchEx(prog_id)
                    try:
                        app.Visible = False
                    except Exception:
                        pass
                    try:
                        app.DisplayAlerts = False
                    except Exception:
                        pass
                    self.logger.info(f"Office-Warm-up erfolgreich: {label}")
                except Exception as exc:
                    warnings.append(f"{label}: {exc}")
                finally:
                    if app is not None:
                        try:
                            app.Quit()
                        except Exception:
                            pass
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

        if warnings:
            message = "Office-Warm-up mit Warnungen: " + "; ".join(warnings)
            self.logger.warning(message)
            return {"success": False, "warning": message}

        return {"success": True, "message": "Office-Warm-up erfolgreich."}
        
    def configure_all_settings(self, config, include_windows: bool = True):
        """Alle Office-Einstellungen konfigurieren"""
        try:
            self.logger.info("Konfiguration der Office-Einstellungen...")
            # Laufbezogenen Zähler zurücksetzen, damit applied_count pro Ausführung korrekt ist
            self.applied_settings = []

            com_bootstrap = self._bootstrap_office_com(config)
            self.logger.info(
                "[COM-HEALTH] PRECHECK | %s",
                com_bootstrap.get("summary", "Word, Excel, Outlook COM vorab initialisiert."),
            )
            
            font_name = config.get("font_name", "Aptos")
            font_size_word = config.get("font_size_word", 11)
            font_size_excel = config.get("font_size_excel", 10)

            # Zielpfad aus GUI-Auswahl berechnen
            use_documents = config.get("use_documents_folder", False)
            if use_documents:
                target_path = str(Path.home() / "Documents")
            else:
                drive = config.get("target_drive", "")
                if drive:
                    target_path = drive if drive.endswith("\\") else drive + "\\"
                else:
                    target_path = config.get("target_path", "")
            
            # Word konfigurieren
            word_result = self.configure_word(font_name, font_size_word, target_path, com_bootstrap=com_bootstrap)
            if not word_result["success"]:
                return word_result
                
            # Excel konfigurieren
            excel_result = self.configure_excel(font_name, font_size_excel, target_path, com_bootstrap=com_bootstrap)
            if not excel_result["success"]:
                return excel_result

            # Outlook konfigurieren (Registry + COM-Sync, soweit verfügbar)
            outlook_result = self.configure_outlook(font_name, font_size_word, com_bootstrap=com_bootstrap)
            if not outlook_result["success"]:
                return outlook_result

            sync_warnings: list[str] = []
            for label, section in (("Word", word_result), ("Excel", excel_result), ("Outlook", outlook_result)):
                warning_text = section.get("com_warning")
                if warning_text:
                    sync_warnings.append(f"{label}: {warning_text}")
                
            # Outlook-Vorlagen kopieren
            outlook_warning = None
            template_result = self.copy_outlook_templates(com_bootstrap=com_bootstrap)
            if not template_result["success"]:
                outlook_warning = template_result.get("error", "Outlook-Vorlage nicht gefunden")
                self.logger.warning(f"Outlook-Konfiguration fehlgeschlagen: {outlook_warning}")
            elif template_result.get("warning"):
                outlook_warning = template_result.get("warning")
                self.logger.warning(f"Outlook-Konfiguration mit Warnung: {outlook_warning}")
            else:
                self.logger.info("Outlook-Template-Schritt erfolgreich abgeschlossen (Kopie + Synchronisation).")

            if outlook_result.get("com_warning"):
                warning_text = outlook_result.get("com_warning")
                if outlook_warning:
                    outlook_warning = f"{outlook_warning}; {warning_text}"
                else:
                    outlook_warning = warning_text

            if outlook_result.get("warning"):
                warning_text = outlook_result.get("warning")
                if outlook_warning:
                    outlook_warning = f"{outlook_warning}; {warning_text}"
                else:
                    outlook_warning = warning_text

            windows_result = {"success": True, "message": "Windows-Einstellungen übersprungen"}
            windows_warning = None
            if include_windows:
                show_hidden_items = self._is_truthy(config.get("show_hidden_items", False))
                windows_result = self.configure_windows_settings(show_hidden_items=show_hidden_items)
                windows_warning = windows_result.get("warning")
                if not windows_result.get("success", False):
                    windows_warning = windows_result.get(
                        "error",
                        "Windows-Einstellungen konnten nicht vollständig gesetzt werden."
                    )
                    self.logger.warning(f"Windows-Konfiguration teilweise fehlgeschlagen: {windows_warning}")

            if com_bootstrap.get("skip_com"):
                sync_warnings = []
                self.logger.info("[COM-HEALTH] OK | COM optional nicht verfügbar; Registry/Template wurden dennoch gesetzt.")
            elif sync_warnings:
                self.logger.warning("[COM-HEALTH] DEGRADED | " + " | ".join(sync_warnings))
            else:
                self.logger.info("[COM-HEALTH] OK | Word/Excel via COM synchronisiert; Outlook via Registry/MailSettings/Template gesetzt")

            new_outlook_notice = self._get_new_outlook_notice()
            if new_outlook_notice:
                self.logger.info(f"[OUTLOOK-MODERN] {new_outlook_notice}")
            
            return {
                "success": True,
                "message": "Office-Einstellungen erfolgreich konfiguriert",
                "applied_count": len(self.applied_settings),
                "word_start_screen_disabled": bool(word_result.get("word_start_screen_disabled", False)),
                "outlook_warning": outlook_warning,
                "windows_configured": bool(windows_result.get("success", False)),
                "windows_warning": windows_warning,
                "com_sync_ok": len(sync_warnings) == 0,
                "com_sync_warning": None if com_bootstrap.get("skip_com") else ("; ".join(sync_warnings) if sync_warnings else None),
                "com_precheck_summary": com_bootstrap.get("summary"),
                "com_precheck_skipped": bool(com_bootstrap.get("skip_com")),
                "outlook_modern_notice": new_outlook_notice,
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Office-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_word(self, font_name="Aptos", font_size=11, target_path="", com_bootstrap: dict | None = None):
        """Word-spezifische Einstellungen konfigurieren"""
        try:
            self.logger.info(f"Word konfigurieren: Schriftart={font_name}, Größe={font_size}")
            
            # Word Registry-Einstellungen mit Erläuterungen
            word_settings = {
                "DeveloperTools": (1, "word_developer_tools"),
                "Ruler": (1, "word_ruler"), 
                "ShowAllFormatting": (1, "word_show_all_formatting"),
                "VisiDrawTableDrs": (1, "word_table_gridlines"),
                "DOC-PATH": (target_path, "word_doc_path"),
                # Autokorrektur-Optionen:
                "CorrectCapsLock": (0, "word_correct_initial_caps"),
                "CorrectSentenceCaps": (0, "word_correct_sentence_caps"),
                "AutoFormatAsYouTypeApplyBulletedLists": (0, "word_auto_bullets"),
                "AutoFormatAsYouTypeApplyNumberedLists": (0, "word_auto_numbering"),
                "AutoFormatApplyBulletedLists": (0, "word_auto_bullets_compat"),
                "AutoFormatApplyNumberedLists": (0, "word_auto_numbering_compat"),
                "AutoFormatCapitalizeTableCells": (0, "word_capitalize_table_cells"),
                "CorrectTableCells": (0, "word_capitalize_table_cells_compat"),
                "PictureInsertLayout": (1, "word_picture_insert_inline"),
                "AutoFormatAsYouTypeReplaceQuotes": (1, "word_smart_quotes"),
                "PasteFormattingOtherApp": (2, "word_paste_other_app"),
                "PasteFormattingTwoDocumentsNoStyles": (1, "word_paste_text_only_keep_lists"),
                # Schriftart-Anzeige und Ersetzungen:
                "Font": (font_name, "word_font_override"),
                "Fontsubstitutes": ("", "word_font_substitutes"),
                # Persönliche Vorlagen:
                "PersonalTemplates": (self._get_datei_vorlagen_path(target_path), "word_personal_templates"),
            }

            # Schriftart-Einstellungen
            font_settings = {
                "Default Font": (font_name, "word_default_font"),
                "Default Font Size": (font_size, "word_default_font_size")
            }
            
            # Registry-Einstellungen anwenden
            self._apply_word_registry_settings(word_settings, font_settings)

            # Build-/Profilabhängig ignoriert Word einzelne DWORD-Werte aus \Word\Options
            # und verwendet stattdessen interne Optionen (Word.Options / Data\Settings).
            # Deshalb zusätzlich per COM setzen und in Normal.dotm persistieren.
            com_warning = None
            if not (com_bootstrap or {}).get("skip_com"):
                com_warning = self._apply_word_options_via_com()
            else:
                self.logger.info("Word-COM übersprungen (Precheck meldete COM nicht verfügbar).")

            # Word-Startbildschirm deaktivieren (direkt in leeres Dokument starten)
            for version in ["16.0", "15.0"]:
                general_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Common\\General"
                self._set_registry_values_with_explanation(
                    winreg.HKEY_CURRENT_USER,
                    general_key_path,
                    {"DisableBootToOfficeStart": (1, "word_disable_start_screen")},
                    "Word",
                    version,
                )

            # Angewandte Einstellungen protokollieren
            self._log_applied_settings("Word")

            return {
                "success": True,
                "message": "Word erfolgreich konfiguriert",
                "word_start_screen_disabled": True,
                "com_warning": com_warning,
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Word-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_excel(self, font_name="Aptos", font_size=10, target_path="", com_bootstrap: dict | None = None):
        """Excel-spezifische Einstellungen konfigurieren"""
        try:
            self.logger.info(f"Excel konfigurieren: Schriftart={font_name}, Größe={font_size}")
            
            # Excel Registry-Einstellungen mit Erläuterungen
            excel_settings = {
                "EXCEL-PATH": (target_path, "excel_path"),
                # Schriftart-Anzeige:
                "Font": (f"{font_name},{font_size}", "excel_font_override"),
                # Persönliche Vorlagen:
                "PersonalTemplates": (self._get_datei_vorlagen_path(target_path), "excel_personal_templates"),
                # Alternative Startup-Verzeichnis für Templates:
                "AltStartupPath": (self._get_datei_vorlagen_path(target_path), "excel_xlstart_info"),
                # Autokorrektur / AutoWiederherstellen:
                "CorrectSentenceCap": (0, "excel_correct_sentence_cap"),
                "AutoSaveInterval": (5, "excel_autosave_interval"),
            }
            
            # Schriftart-Einstellungen
            font_settings = {
                "Default Font": (font_name, "excel_default_font"),
                "Default Font Size": (font_size, "excel_default_font_size")
            }
            
            # Registry-Einstellungen anwenden
            self._apply_excel_registry_settings(excel_settings, font_settings)

            # Registry-Werte zusätzlich mit Excel-COM synchronisieren
            com_warning = None
            if not (com_bootstrap or {}).get("skip_com"):
                com_warning = self._apply_excel_options_via_com(font_name, font_size)
            else:
                self.logger.info("Excel-COM übersprungen (Precheck meldete COM nicht verfügbar).")
            
            # Angewandte Einstellungen protokollieren
            self._log_applied_settings("Excel")
            
            result = {"success": True, "message": "Excel erfolgreich konfiguriert"}
            if com_warning:
                result["com_warning"] = com_warning
            return result
            
        except Exception as e:
            self.logger.error(f"Fehler bei Excel-Konfiguration: {e}")
            return {"success": False, "error": str(e)}

    def configure_outlook(self, font_name="Aptos", font_size=11, com_bootstrap: dict | None = None):
        """Outlook-spezifische Registry/COM-Einstellungen konfigurieren."""
        try:
            self.logger.info(f"Outlook konfigurieren: Schriftart={font_name}, Größe={font_size}")

            outlook_settings = {
                "NewMailFont": (font_name, "outlook_new_mail_font"),
                "NewMailFontSize": (int(font_size), "outlook_new_mail_font_size"),
                "ReplyForwardFont": (font_name, "outlook_reply_forward_font"),
                "ReplyForwardFontSize": (int(font_size), "outlook_reply_forward_font_size"),
                "DefaultMailFont": (font_name, "outlook_default_mail_font_legacy"),
            }

            office_versions = ["16.0", "15.0"]
            for version in office_versions:
                key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Outlook\\Options"
                self._set_registry_values_with_explanation(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    outlook_settings,
                    "Outlook",
                    version,
                )

            mailsettings_warning = self._apply_outlook_mailsettings_registry(font_name, int(font_size))

            com_warning = None
            self.logger.info(
                "Outlook-COM-Synchronisierung wird übersprungen: MailSettings + Template-Sync sind der primäre und schnellere Pfad."
            )
            self._log_applied_settings("Outlook")

            result = {"success": True, "message": "Outlook erfolgreich konfiguriert"}
            if mailsettings_warning:
                result["warning"] = mailsettings_warning
            if com_warning:
                result["com_warning"] = com_warning
            return result
        except Exception as e:
            self.logger.error(f"Fehler bei Outlook-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    

    def copy_outlook_templates(self, com_bootstrap: dict | None = None):
        """Outlook-Vorlagen kopieren und die Zielvorlage mit der registrierten Schrift synchronisieren."""
        try:
            self.logger.info("Outlook-Vorlagen werden kopiert...")

            # Outlook-Benutzerverzeichnis finden
            outlook_templates_dir = self._get_outlook_templates_dir()
            if not outlook_templates_dir:
                return {"success": False, "error": "Outlook-Vorlagenverzeichnis nicht gefunden"}

            # Quell-Template-Datei aus Unterordner 'Sonstiges/Standards'
            runtime_root = os.environ.get('PCONFIG_RUNTIME_ROOT', '').strip()
            if runtime_root:
                base_dir = Path(runtime_root)
            else:
                import sys
                if getattr(sys, 'frozen', False):
                    # Fallback: EXE-Verzeichnis
                    base_dir = Path(sys.executable).parent
                else:
                    # Ausgeführt als Script: Projektwurzel liegt i.d.R. eine Ebene über src/
                    base_dir = Path(__file__).resolve().parent.parent

            source_candidates = [
                base_dir / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm",
            ]

            # Zusätzliche Fallback-Kandidaten für Direkt-/Terminal-Läufe
            source_candidates.extend([
                Path(__file__).resolve().parent / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm",
                Path.cwd() / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm",
            ])

            # Fallback: direkt aus dem PyInstaller-Bundle lesen, falls Runtime-Datei gesperrt ist
            import sys
            meipass = getattr(sys, '_MEIPASS', None)
            if meipass:
                source_candidates.append(Path(meipass) / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm")

            target_path = outlook_templates_dir / "NormalEmail.dotm"
            target_path.parent.mkdir(parents=True, exist_ok=True)

            last_error = None
            for source_template in source_candidates:
                if not source_template.exists():
                    continue

                # Einige OneDrive-/Runtimeszenarien setzen Dateien auf read-only.
                # Lesen klappt meist trotzdem, wir versuchen es hier proaktiv robuster zu machen.
                try:
                    os.chmod(source_template, 0o666)
                except Exception:
                    pass

                for attempt in range(1, 4):
                    try:
                        shutil.copy2(source_template, target_path)
                        self.logger.info(f"Outlook-Vorlage kopiert: {source_template} -> {target_path}")
                        self.logger.info("Outlook-Template wird nun mit der aktuell gesetzten Schrift synchronisiert...")
                        sync_warning = self._sync_outlook_template_from_registry(
                            target_path,
                            allow_com_fallback=not (com_bootstrap or {}).get("skip_com"),
                        )
                        result = {"success": True, "message": "Outlook-Vorlagen erfolgreich kopiert"}
                        if sync_warning:
                            self.logger.warning(f"Outlook-Template-Synchronisation mit Hinweis: {sync_warning}")
                            result["warning"] = sync_warning
                        else:
                            self.logger.info("Outlook-Template-Synchronisation erfolgreich abgeschlossen.")
                        return result
                    except PermissionError as e:
                        last_error = e
                        self.logger.warning(
                            f"Permission-Problem beim Kopieren von Outlook-Vorlage (Versuch {attempt}/3): {e}"
                        )
                        time.sleep(0.7)
                    except Exception as e:
                        last_error = e
                        self.logger.warning(
                            f"Fehler beim Kopieren von Outlook-Vorlage aus {source_template} (Versuch {attempt}/3): {e}"
                        )
                        time.sleep(0.4)

            if last_error is not None:
                return {"success": False, "error": str(last_error)}

            self.logger.warning("Quell-Template nicht gefunden (NormalEmail.dotm).")
            return {"success": False, "error": "Outlook-Vorlage nicht gefunden"}

        except Exception as e:
            self.logger.error(f"Fehler beim Kopieren der Outlook-Vorlagen: {e}")
            return {"success": False, "error": str(e)}

    def _get_outlook_font_from_registry(self):
        """Liest die zuletzt konfigurierte Outlook-Schrift aus der Benutzer-Registry."""
        candidates = ["16.0", "15.0", "14.0"]
        font_value_names = ["NewMailFont", "DefaultMailFont", "ReplyForwardFont"]
        size_value_names = ["NewMailFontSize", "ReplyForwardFontSize"]

        for version in candidates:
            mailsettings_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Common\\MailSettings"
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, mailsettings_key_path, 0, winreg.KEY_READ) as key:
                    for value_name in ("ComposeFontComplex", "ReplyFontComplex", "TextFontComplex"):
                        try:
                            blob, reg_type = winreg.QueryValueEx(key, value_name)
                            if reg_type == winreg.REG_BINARY and isinstance(blob, (bytes, bytearray)):
                                parsed = self._extract_outlook_font_from_complex_blob(bytes(blob))
                                if parsed:
                                    font_name, font_size = parsed
                                    return font_name, font_size, version
                        except FileNotFoundError:
                            continue
            except FileNotFoundError:
                pass
            except Exception as exc:
                self.logger.debug(f"Outlook-MailSettings konnte nicht gelesen werden ({version}): {exc}")

            key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Outlook\\Options"
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                    font_name = None
                    font_size = None

                    for value_name in font_value_names:
                        try:
                            current, reg_type = winreg.QueryValueEx(key, value_name)
                            if reg_type == winreg.REG_SZ and str(current).strip():
                                font_name = str(current).strip()
                                break
                        except FileNotFoundError:
                            continue

                    for value_name in size_value_names:
                        try:
                            current, reg_type = winreg.QueryValueEx(key, value_name)
                            if reg_type == winreg.REG_DWORD:
                                font_size = int(current)
                                break
                        except FileNotFoundError:
                            continue

                    if font_name and font_size:
                        return font_name, font_size, version
            except FileNotFoundError:
                continue
            except Exception as exc:
                self.logger.debug(f"Outlook-Registry konnte nicht gelesen werden ({version}): {exc}")

        return None, None, None

    def _extract_outlook_font_from_complex_blob(self, blob: bytes):
        """Extrahiert Schriftname/-größe aus Outlook *FontComplex*-HTML-Binärwerten."""
        try:
            text = blob.decode("utf-8", errors="ignore")

            font_match = re.search(r'font-family:\s*"([^"]+)"', text, flags=re.IGNORECASE)
            if not font_match:
                return None

            size_match = re.search(r'font-size:\s*([0-9]+(?:\.[0-9]+)?)pt', text, flags=re.IGNORECASE)
            if not size_match:
                return None

            font_name = font_match.group(1).strip()
            font_size = int(round(float(size_match.group(1))))
            if not font_name or font_size <= 0:
                return None
            return font_name, font_size
        except Exception:
            return None

    def _build_outlook_font_simple_blob(self, font_name: str, font_size: int) -> bytes:
        """Erzeugt einen einfachen Outlook-Font-Blob (Compose/Reply/Text *Simple*)."""
        safe_size = max(1, min(int(font_size), 72))
        safe_name = (font_name or "Aptos").strip() or "Aptos"

        blob = bytearray(60)
        blob[:12] = bytes.fromhex("3C0000001F0000F800000040")
        blob[12:16] = int(safe_size * 20).to_bytes(4, "little", signed=False)
        blob[27] = 0x22

        try:
            encoded_name = safe_name.encode("mbcs", errors="replace")
        except LookupError:
            encoded_name = safe_name.encode("latin-1", errors="replace")

        encoded_name = encoded_name[:31]
        start = 28
        blob[start:start + len(encoded_name)] = encoded_name
        blob[start + len(encoded_name)] = 0
        return bytes(blob)

    def _build_outlook_font_complex_blob(self, font_name: str, font_size: int, mode: str) -> bytes:
        """Erzeugt einen Outlook-*FontComplex*-Blob als HTML/CSS."""
        safe_size = max(1, min(int(font_size), 72))
        safe_name = (font_name or "Aptos").replace('"', "'").strip() or "Aptos"

        if mode == "compose":
            selector = "span.PersönlicherErstellstil"
            style_name = "Persönlicher Erstellstil"
            style_type = "personal-compose"
        elif mode == "reply":
            selector = "span.PersönlicherAntwortstil1"
            style_name = "Persönlicher Antwortstil1"
            style_type = "personal-reply"
        else:
            selector = "p.MsoPlainText, li.MsoPlainText, div.MsoPlainText"
            style_name = "Nur Text"
            style_type = "plain-text"

        html = (
            "<html>\r\n\r\n"
            "<head>\r\n"
            "<style>\r\n\r\n"
            "<!--\r\n"
            " /* Style Definitions */\r\n"
            f" {selector}\r\n"
            "\t{"
            f"mso-style-name:\"{style_name}\";"
            f"mso-style-type:{style_type};"
            "mso-style-noshow:yes;"
            "mso-style-unhide:no;"
            f"font-size:{safe_size}.0pt;"
            f"mso-ansi-font-size:{safe_size}.0pt;"
            f"mso-bidi-font-size:{safe_size}.0pt;"
            f"font-family:\"{safe_name}\",sans-serif;"
            f"mso-ascii-font-family:{safe_name};"
            f"mso-fareast-font-family:{safe_name};"
            f"mso-hansi-font-family:{safe_name};"
            "mso-bidi-font-family:\"Times New Roman\";"
            f"font-family:\"{safe_name}\",sans-serif!important;"
            f"font-size:{safe_size}.0pt!important;"
            "color:windowtext;"
            "}\r\n"
            "-->\r\n"
            "</style>\r\n"
            "</head>\r\n\r\n"
            "</html>\r\n"
        )
        return html.encode("utf-8", errors="replace")

    def _apply_outlook_mailsettings_registry(self, font_name: str, font_size: int) -> str | None:
        """Setzt Outlook-Schriftwerte im Common\\MailSettings-Zweig (COM-freier Hauptpfad)."""
        office_versions = ["16.0", "15.0"]
        errors: list[str] = []

        value_map = {
            "ComposeFontSimple": self._build_outlook_font_simple_blob(font_name, font_size),
            "ReplyFontSimple": self._build_outlook_font_simple_blob(font_name, font_size),
            "TextFontSimple": self._build_outlook_font_simple_blob(font_name, font_size),
            "ComposeFontComplex": self._build_outlook_font_complex_blob(font_name, font_size, "compose"),
            "ReplyFontComplex": self._build_outlook_font_complex_blob(font_name, font_size, "reply"),
            "TextFontComplex": self._build_outlook_font_complex_blob(font_name, font_size, "text"),
        }

        for version in office_versions:
            key_paths = [
                f"SOFTWARE\\Microsoft\\Office\\{version}\\Common\\MailSettings",
                f"SOFTWARE\\Microsoft\\Office\\{version}\\Outlook\\Options\\Mail",
            ]
            try:
                for key_path in key_paths:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        for value_name, blob in value_map.items():
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_BINARY, blob)

                self.logger.info(
                    "[Outlook %s] MailSettings aktualisiert (Common + Outlook\\Options\\Mail): %s %dpt (Simple+Complex)",
                    version,
                    font_name,
                    int(font_size),
                )
            except Exception as exc:
                errors.append(f"{version}: {exc}")

        if errors:
            warning = "Outlook-MailSettings konnten nicht vollständig gesetzt werden (" + "; ".join(errors) + ")"
            self.logger.warning(warning)
            return warning
        return None

    def _sync_outlook_template_from_registry(self, template_path: Path, allow_com_fallback: bool = True):
        """Passt die Outlook-Vorlage an die eben gesetzte Schrift aus der Registry an."""
        font_name, font_size, version = self._get_outlook_font_from_registry()
        if not font_name or not font_size:
            self.logger.warning("Outlook-Template-Synchronisation übersprungen: Schrift konnte aus der Registry nicht ermittelt werden.")
            return "Outlook-Schrift konnte aus der Registry nicht ermittelt werden."

        try:
            from pcconfig.safe_template_processor import SafeTemplateProcessor

            processor = SafeTemplateProcessor()
            if processor.update_word_template_xml(template_path, font_name, font_size):
                self.logger.info(
                    "Outlook-Vorlage synchronisiert: %s → %s %dpt (Office %s)",
                    template_path,
                    font_name,
                    font_size,
                    version,
                )
                return None

            if allow_com_fallback:
                self.logger.warning(
                    "XML-Synchronisierung für Outlook-Vorlage fehlgeschlagen, versuche COM-Fallback: %s",
                    template_path,
                )
            else:
                self.logger.info(
                    "XML-Synchronisierung für Outlook-Vorlage fehlgeschlagen; COM-Fallback wird wegen Precheck übersprungen: %s",
                    template_path,
                )

            if allow_com_fallback and processor.update_word_template_safely(template_path, font_name, font_size):
                self.logger.info(
                    "Outlook-Vorlage per COM synchronisiert: %s → %s %dpt (Office %s)",
                    template_path,
                    font_name,
                    font_size,
                    version,
                )
                return None

            return None if not allow_com_fallback else f"Outlook-Vorlage konnte nicht auf {font_name} {font_size}pt aktualisiert werden."
        except Exception as exc:
            self.logger.warning(f"Outlook-Vorlagen-Synchronisierung fehlgeschlagen: {exc}")
            return f"Outlook-Vorlagen-Synchronisierung fehlgeschlagen: {exc}"
    
    def _apply_word_registry_settings(self, word_settings, font_settings):
        """Word Registry-Einstellungen anwenden"""
        try:
            # Word-Versionen finden
            office_versions = ["16.0", "15.0"]  # Office 2016/2019/2021 und Office 2013
            
            for version in office_versions:
                try:
                    # Haupt-Einstellungen
                    key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options"
                    self._set_registry_values_with_explanation(winreg.HKEY_CURRENT_USER, key_path, word_settings, "Word", version)
                    
                    # Font-Einstellungen
                    font_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Data"
                    self._set_registry_values_with_explanation(winreg.HKEY_CURRENT_USER, font_key_path, font_settings, "Word", version)
                    
                    self.logger.info(f"Word {version} Registry-Einstellungen angewendet")
                    
                except Exception as e:
                    self.logger.debug(f"Fehler bei Word {version} Registry: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Fehler bei Word Registry-Einstellungen: {e}")
            raise

    def _apply_word_options_via_com(self) -> str | None:
        """Setzt kritische Word-AutoFormat-Optionen direkt über COM.

        Hintergrund: Auf manchen Office-Builds (insb. mit Roaming-Profilen) spiegelt
        die UI diese Optionen nicht aus den einfachen DWORD-Keys unter
        HKCU\\...\\Word\\Options, sondern aus internen Word-Optionen.
        """
        try:
            import win32com.client  # type: ignore

            word = win32com.client.Dispatch("Word.Application")
            try:
                options = word.Options
                options.AutoFormatAsYouTypeApplyBulletedLists = False
                options.AutoFormatAsYouTypeApplyNumberedLists = False
                options.AutoFormatApplyBulletedLists = False
                options.AutoFormatApplyLists = False
                options.AutoFormatAsYouTypeFormatListItemBeginning = False

                try:
                    word.NormalTemplate.Save()
                except Exception as save_error:
                    self.logger.warning(f"NormalTemplate konnte nicht gespeichert werden: {save_error}")

                self.logger.info("Word AutoFormat-Optionen zusätzlich per COM synchronisiert")
                return None
            finally:
                try:
                    word.Quit()
                except Exception:
                    pass
        except Exception as e:
            # Nicht hart fehlschlagen lassen: Registry-Teil ist bereits gesetzt.
            self.logger.warning(f"COM-Synchronisierung für Word-Optionen fehlgeschlagen: {e}")
            return "Word-COM nicht verfügbar (Registry wurde dennoch gesetzt)."

    def _apply_excel_options_via_com(self, font_name: str, font_size: int) -> str | None:
        """Setzt kritische Excel-Optionen ergänzend per COM."""
        try:
            import win32com.client  # type: ignore

            excel = win32com.client.Dispatch("Excel.Application")
            try:
                try:
                    excel.StandardFont = font_name
                    excel.StandardFontSize = int(font_size)
                except Exception as font_error:
                    self.logger.warning(f"Excel-Standardfont via COM nicht gesetzt: {font_error}")

                try:
                    autocorrect = excel.AutoCorrect
                    autocorrect.CorrectSentenceCap = False
                except Exception as autocorrect_error:
                    self.logger.warning(f"Excel AutoCorrect via COM nicht gesetzt: {autocorrect_error}")

                try:
                    autorecover = excel.AutoRecover
                    autorecover.Time = 5
                    autorecover.Enabled = True
                except Exception as autorecover_error:
                    self.logger.warning(f"Excel AutoRecover via COM nicht gesetzt: {autorecover_error}")

                self.logger.info("Excel-Optionen zusätzlich per COM synchronisiert")
                return None
            finally:
                try:
                    excel.Quit()
                except Exception:
                    pass
        except Exception as e:
            self.logger.warning(f"COM-Synchronisierung für Excel-Optionen fehlgeschlagen: {e}")
            return "Excel-COM nicht verfügbar (Registry wurde dennoch gesetzt)."

    def _apply_outlook_options_via_com(self, font_name: str, font_size: int) -> str | None:
        """Versucht Outlook-Optionen zusätzlich per COM zu synchronisieren.

        Gibt eine Warnung zurück, wenn COM auf dem System nicht verfügbar ist.
        """
        try:
            import win32com.client  # type: ignore

            outlook = win32com.client.Dispatch("Outlook.Application")
            try:
                options_obj = getattr(outlook, "Options", None)
                if options_obj is None:
                    self.logger.info("Outlook COM verfügbar, aber kein Options-Objekt gefunden")
                    return "Outlook-COM ohne Options-Objekt (Registry wurde dennoch gesetzt)."

                # Property-Namen variieren zwischen Outlook-Versionen stark.
                candidates = {
                    "NewMailFont": ["NewMailFont", "NewMailFontName"],
                    "NewMailFontSize": ["NewMailFontSize"],
                    "ReplyForwardFont": ["ReplyForwardFont", "ReplyForwardFontName"],
                    "ReplyForwardFontSize": ["ReplyForwardFontSize"],
                }
                values = {
                    "NewMailFont": font_name,
                    "NewMailFontSize": int(font_size),
                    "ReplyForwardFont": font_name,
                    "ReplyForwardFontSize": int(font_size),
                }

                set_count = 0
                for logical_name, prop_names in candidates.items():
                    for prop_name in prop_names:
                        try:
                            setattr(options_obj, prop_name, values[logical_name])
                            set_count += 1
                            break
                        except Exception:
                            continue

                self.logger.info(f"Outlook-Optionen per COM synchronisiert (gesetzte Properties: {set_count})")
                return None
            finally:
                try:
                    outlook.Quit()
                except Exception:
                    pass
        except Exception as e:
            self.logger.warning(f"COM-Synchronisierung für Outlook-Optionen fehlgeschlagen: {e}")
            return "Outlook-COM auf diesem System nicht verfügbar (Registry wurde dennoch gesetzt)."
    
    def _apply_excel_registry_settings(self, excel_settings, font_settings):
        """Excel Registry-Einstellungen anwenden"""
        try:
            # Excel-Versionen finden
            office_versions = ["16.0", "15.0"]  # Office 2016/2019/2021 und Office 2013
            
            for version in office_versions:
                try:
                    # Haupt-Einstellungen
                    key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options"
                    self._set_registry_values_with_explanation(winreg.HKEY_CURRENT_USER, key_path, excel_settings, "Excel", version)
                    
                    # Font-Einstellungen
                    font_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Data"
                    self._set_registry_values_with_explanation(winreg.HKEY_CURRENT_USER, font_key_path, font_settings, "Excel", version)
                    
                    self.logger.info(f"Excel {version} Registry-Einstellungen angewendet")
                    
                except Exception as e:
                    self.logger.debug(f"Fehler bei Excel {version} Registry: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Fehler bei Excel Registry-Einstellungen: {e}")
            raise

    def configure_windows_settings(self, show_hidden_items: bool = False):
        """Windows-Explorer- und Taskleisten-Defaults konfigurieren."""
        try:
            self.logger.info("Windows-Einstellungen werden konfiguriert...")

            hidden_value = 1 if show_hidden_items else 2
            show_super_hidden_value = 1 if show_hidden_items else 0
            self.logger.info(
                "Explorer-Sichtbarkeit: ausgeblendete Elemente %s",
                "anzeigen" if show_hidden_items else "ausblenden",
            )

            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            windows_settings = [
                ("TaskbarAl", 0, "windows_taskbar_alignment"),
                ("TaskbarDa", 0, "windows_hide_widgets"),
                ("SearchboxTaskbarMode", 0, "windows_hide_searchbox"),
                ("HideFileExt", 0, "windows_explorer_show_extensions"),
                ("Hidden", hidden_value, "windows_explorer_show_hidden_items"),
                ("SearchFileNameAlways", 1, "windows_explorer_search_file_contents"),
                ("ShowRecent", 0, "windows_explorer_show_recent_files"),
            ]
            failed_values: list[str] = []

            start_menu_settings = [
                ("Start_Layout", 1, "windows_startmenu_list_layout"),
                ("Start_TrackProgs", 1, "windows_startmenu_list_view"),
                ("Start_TrackDocs", 0, "windows_startmenu_track_documents"),
                ("Start_ShowDocuments", 1, "windows_startmenu_show_documents"),
                ("Start_ShowDownloads", 1, "windows_startmenu_show_downloads"),
                ("Start_ShowNetwork", 1, "windows_startmenu_show_network"),
                ("Start_ShowFileExplorer", 1, "windows_startmenu_show_file_explorer"),
                ("Start_ShowSettings", 1, "windows_startmenu_show_settings"),
                ("Start_ShowPowerButton", 1, "windows_startmenu_show_power"),
            ]

            for name, value, explanation_key in windows_settings:
                if not self._set_windows_value_with_fallback(key_path, name, value, explanation_key):
                    failed_values.append(name)

            for name, value, explanation_key in start_menu_settings:
                if not self._set_windows_value_with_fallback(key_path, name, value, explanation_key):
                    failed_values.append(name)

            # Moderne Windows-Builds steuern die im Start sichtbaren Ordner teils über
            # den Binary-Wert "VisiblePlaces" im Start-Zweig. Dieser Wert ist
            # systemspezifisch kodiert und wird hier bewusst nicht blind überschrieben.
            start_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Start"
            visible_places_exists = self._read_registry_value(winreg.HKEY_CURRENT_USER, start_key_path, "VisiblePlaces") is not None
            if visible_places_exists:
                self.logger.info(
                    "Startmenü-Ordnersymbole werden auf diesem System zusätzlich über "
                    "'CurrentVersion\\Start\\VisiblePlaces' gesteuert (Build-spezifisch)."
                )

            # Zusatzwerte ohne RegistryExplainer-Mapping
            extra_values = {
                "ShowSuperHidden": show_super_hidden_value
            }
            for name, value in extra_values.items():
                if not self._set_windows_extra_value_with_fallback(key_path, name, value):
                    failed_values.append(name)

            # Suchfeld/Suchsymbol zusätzlich im Search-Zweig setzen
            # (einige Windows-Builds werten diesen Pfad bevorzugt aus)
            search_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
            if not self._set_windows_extra_value_with_fallback(search_key_path, "SearchboxTaskbarMode", 0):
                failed_values.append("SearchboxTaskbarMode")

            # Optionaler Cache-Wert für konsistentere UI-Übernahme nach Explorer-Neustart
            self._set_windows_extra_value_with_fallback(search_key_path, "SearchboxTaskbarModeCache", 0)

            # Taskleisten-Ausrichtung hart verifizieren (einige Systeme überschreiben den Wert sofort)
            taskbar_al = self._read_dword_registry_value(winreg.HKEY_CURRENT_USER, key_path, "TaskbarAl")
            if taskbar_al != 0:
                self.logger.warning(
                    f"TaskbarAl nach Setzen unerwartet: {taskbar_al}. Fallback via reg.exe wird versucht."
                )
                subprocess.run(
                    [
                        "reg",
                        "add",
                        r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                        "/v",
                        "TaskbarAl",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "0",
                        "/f",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                taskbar_al = self._read_dword_registry_value(winreg.HKEY_CURRENT_USER, key_path, "TaskbarAl")

            if taskbar_al != 0:
                if "TaskbarAl" not in failed_values:
                    failed_values.append("TaskbarAl")

            if failed_values:
                unique_failed = sorted(set(failed_values))

                # TaskbarDa (Widgets) ist optional und kann in einigen Umgebungen
                # per Richtlinie gesperrt sein, ohne die Kernziele zu blockieren.
                optional_values = {
                    "TaskbarDa",
                    "Start_TrackProgs",
                    "Start_ShowDocuments",
                    "Start_ShowDownloads",
                    "Start_ShowNetwork",
                    "Start_ShowFileExplorer",
                    "Start_ShowSettings",
                    "Start_ShowPowerButton",
                }
                blocking_failed = [name for name in unique_failed if name not in optional_values]

                if not blocking_failed:
                    return {
                        "success": True,
                        "warning": (
                            "Ein optionaler Windows-Wert konnte nicht gesetzt werden "
                            f"(nicht gesetzt: {', '.join(unique_failed)})."
                        ),
                        "message": "Windows-Kerneinstellungen erfolgreich konfiguriert",
                    }

                return {
                    "success": False,
                    "error": (
                        "Windows-Einstellungen teilweise blockiert (mögliche Richtlinie/Berechtigung). "
                        f"Nicht gesetzt: {', '.join(blocking_failed)}"
                    ),
                }

            return {"success": True, "message": "Windows-Einstellungen erfolgreich konfiguriert"}
        except Exception as e:
            self.logger.error(f"Fehler bei Windows-Konfiguration: {e}")
            return {"success": False, "error": str(e)}

    def _set_windows_value_with_fallback(self, key_path, name, value, explanation_key):
        """Setzt einen dokumentierten Windows-Wert mit WinReg und reg.exe-Fallback."""
        is_optional_policy_value = name == "TaskbarDa"

        # Optionaler Spezialfall: TaskbarDa ist auf vielen Systemen via Richtlinie gesperrt.
        # Hier bewusst ohne _set_single_registry_value arbeiten, um unnötiges Error-Logging
        # bei Access-Denied zu vermeiden.
        if is_optional_policy_value:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
                self.logger.info(f"[Windows Current] {name} = {value}")
                return True
            except Exception as e:
                if "WinError 5" in str(e):
                    self.logger.info(
                        f"[Windows Current] {name} ist per Richtlinie/Berechtigung geschützt; "
                        "Wert wird als optional übersprungen."
                    )
                    return True

        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                self._set_single_registry_value(
                    key,
                    name,
                    int(value),
                    explanation_key,
                    "Windows",
                    "Current",
                    key_path,
                )
            return True
        except Exception as e:
            if is_optional_policy_value and "WinError 5" in str(e):
                self.logger.info(
                    f"[Windows Current] {name} ist per Richtlinie/Berechtigung geschützt; "
                    "Wert wird als optional übersprungen."
                )
                return True

            self.logger.warning(f"WinReg-Setzen fehlgeschlagen für {name}: {e}. Versuche reg.exe-Fallback...")

            fallback = subprocess.run(
                [
                    "reg",
                    "add",
                    rf"HKCU\{key_path}",
                    "/v",
                    name,
                    "/t",
                    "REG_DWORD",
                    "/d",
                    str(int(value)),
                    "/f",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            if fallback.returncode == 0:
                # Logging analog zu _set_single_registry_value
                setting_info = self.registry_explainer.get_setting_by_name(explanation_key)
                self.logger.info(f"[Windows Current] {name} = {value} (via reg.exe)")
                self.applied_settings.append({
                    "program": "Windows",
                    "version": "Current",
                    "key_path": key_path,
                    "name": name,
                    "value": int(value),
                    "description": setting_info.description if setting_info else "Windows-Einstellung",
                    "impact": setting_info.impact if setting_info else "Windows UI-Verhalten",
                    "category": setting_info.category if setting_info else "Windows - Explorer",
                })
                return True

            if is_optional_policy_value:
                self.logger.info(
                    f"[Windows Current] {name} konnte nicht gesetzt werden (optional/policy), "
                    "ohne Abbruch fortgesetzt."
                )
                return True

            # Falls Schreiben blockiert ist, aber der Zielwert bereits gesetzt ist,
            # darf dies nicht als Fehler gewertet werden.
            current_value = self._read_dword_registry_value(winreg.HKEY_CURRENT_USER, key_path, name)
            if current_value == int(value):
                self.logger.info(
                    f"[Windows Current] {name} bereits korrekt gesetzt ({value}); "
                    "Schreibversuch war nicht erforderlich/zulässig."
                )
                return True

            stderr = (fallback.stderr or "").strip()
            self.logger.warning(f"reg.exe-Fallback fehlgeschlagen für {name}: {stderr}")
            return False

    def _set_windows_extra_value_with_fallback(self, key_path, name, value):
        """Setzt einen zusätzlichen Windows-Wert mit WinReg und reg.exe-Fallback."""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
            self.logger.info(f"[Windows Current] {name} = {value}")
            self.applied_settings.append({
                "program": "Windows",
                "version": "Current",
                "key_path": key_path,
                "name": name,
                "value": int(value),
                "description": "Zusätzliche Explorer-Option",
                "impact": "Verbessert Sichtbarkeit im Explorer",
                "category": "Windows - Explorer",
            })
            return True
        except Exception as e:
            self.logger.warning(f"WinReg-Setzen fehlgeschlagen für {name}: {e}. Versuche reg.exe-Fallback...")
            fallback = subprocess.run(
                [
                    "reg",
                    "add",
                    rf"HKCU\{key_path}",
                    "/v",
                    name,
                    "/t",
                    "REG_DWORD",
                    "/d",
                    str(int(value)),
                    "/f",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if fallback.returncode == 0:
                self.logger.info(f"[Windows Current] {name} = {value} (via reg.exe)")
                self.applied_settings.append({
                    "program": "Windows",
                    "version": "Current",
                    "key_path": key_path,
                    "name": name,
                    "value": int(value),
                    "description": "Zusätzliche Explorer-Option",
                    "impact": "Verbessert Sichtbarkeit im Explorer",
                    "category": "Windows - Explorer",
                })
                return True

            # Bereits korrekt gesetzter Wert => kein Fehler
            current_value = self._read_dword_registry_value(winreg.HKEY_CURRENT_USER, key_path, name)
            if current_value == int(value):
                self.logger.info(
                    f"[Windows Current] {name} bereits korrekt gesetzt ({value}); "
                    "Schreibversuch war nicht erforderlich/zulässig."
                )
                return True

            stderr = (fallback.stderr or "").strip()
            self.logger.warning(f"reg.exe-Fallback fehlgeschlagen für {name}: {stderr}")
            return False

    def _read_dword_registry_value(self, hive, key_path, value_name):
        """Liest einen DWORD-Wert aus der Registry, sonst None."""
        try:
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
                value, reg_type = winreg.QueryValueEx(key, value_name)
                if reg_type == winreg.REG_DWORD:
                    return int(value)
                return None
        except Exception:
            return None

    def _read_registry_value(self, hive, key_path, value_name):
        """Liest einen beliebigen Registry-Wert, sonst None."""
        try:
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
        except Exception:
            return None
    
    def _set_registry_values_with_explanation(self, hive, key_path, values, program, version):
        """Registry-Werte setzen mit detaillierten Erläuterungen"""
        try:
            # Registry-Key öffnen oder erstellen
            try:
                with winreg.OpenKey(hive, key_path, 0, winreg.KEY_WRITE) as key:
                    for name, value_info in values.items():
                        value, explanation_key = value_info
                        self._set_single_registry_value(key, name, value, explanation_key, program, version, key_path)
            except FileNotFoundError:
                # Key existiert nicht, erstellen
                with winreg.CreateKey(hive, key_path) as key:
                    for name, value_info in values.items():
                        value, explanation_key = value_info
                        self._set_single_registry_value(key, name, value, explanation_key, program, version, key_path)
                            
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen der Registry-Werte für {key_path}: {e}")
            raise
    
    def _set_single_registry_value(self, key, name, value, explanation_key, program, version, key_path):
        """Einzelnen Registry-Wert setzen mit Logging"""
        try:
            # Erläuterung abrufen
            setting_info = self.registry_explainer.get_setting_by_name(explanation_key)
            
            # Wert setzen
            if isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            else:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
            
            # Detailliertes Logging
            if setting_info:
                self.logger.info(f"[{program} {version}] {name} = {value}")
                self.logger.info(f"  Beschreibung: {setting_info.description}")
                self.logger.info(f"  Auswirkung: {setting_info.impact}")
                self.applied_settings.append({
                    "program": program,
                    "version": version,
                    "key_path": key_path,
                    "name": name,
                    "value": value,
                    "description": setting_info.description,
                    "impact": setting_info.impact,
                    "category": setting_info.category
                })
            else:
                self.logger.info(f"[{program} {version}] {name} = {value} (keine Erläuterung verfügbar)")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen von {name}: {e}")
            raise
    
    def _get_default_docs_path(self):
        """Standard-Dokumentenpfad ermitteln"""
        try:
            # Z:\ bevorzugen (BFW), sonst Documents
            if os.path.exists("Z:\\"):
                return "Z:\\"
            else:
                return str(Path.home() / "Documents")
        except Exception:
            return str(Path.home() / "Documents")
    
    def _get_datei_vorlagen_path(self, target_path):
        """Datei-Vorlagen-Ordner-Pfad ermitteln (als Unterpfad des Zielverzeichnisses)"""
        try:
            if target_path:
                datei_vorlagen = Path(target_path) / "Datei-Vorlagen"
                return str(datei_vorlagen.resolve())
            else:
                # Fallback auf Standard-Dokumentenpfad
                default_path = self._get_default_docs_path()
                datei_vorlagen = Path(default_path) / "Datei-Vorlagen"
                return str(datei_vorlagen.resolve())
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln des Datei-Vorlagen-Pfads: {e}")
            return str(Path.home() / "Documents" / "Datei-Vorlagen")
    
    def _get_outlook_templates_dir(self):
        """Outlook-Vorlagenverzeichnis ermitteln"""
        try:
            # Standard Outlook-Vorlagenpfad
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                outlook_templates = Path(appdata) / "Microsoft" / "Templates"
                if outlook_templates.exists():
                    return outlook_templates
                    
            # Fallback: Benutzer-Templates-Verzeichnis
            templates_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            return templates_dir
            
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln des Outlook-Vorlagenverzeichnisses: {e}")
            return None
    
    def _log_applied_settings(self, program):
        """Zusammenfassung der angewandten Einstellungen protokollieren"""
        program_settings = [s for s in self.applied_settings if s["program"] == program]
        
        if program_settings:
            self.logger.info(f"=== {program} Konfiguration Zusammenfassung ===")
            for setting in program_settings:
                self.logger.info(f"✓ {setting['name']}: {setting['value']} ({setting['category']})")
            self.logger.info(f"=== {len(program_settings)} {program} Einstellungen angewendet ===")
    
