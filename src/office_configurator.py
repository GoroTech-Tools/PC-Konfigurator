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
from pathlib import Path
from registry_explainer import RegistryExplainer


class OfficeConfigurator:
    """Klasse zur Konfiguration von Office-Programmen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry_explainer = RegistryExplainer()
        self.applied_settings = []  # Track applied settings for logging
        
    def configure_all_settings(self, config):
        """Alle Office-Einstellungen konfigurieren"""
        try:
            self.logger.info("Konfiguration der Office-Einstellungen...")
            # Laufbezogenen Zähler zurücksetzen, damit applied_count pro Ausführung korrekt ist
            self.applied_settings = []
            
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
            word_result = self.configure_word(font_name, font_size_word, target_path)
            if not word_result["success"]:
                return word_result
                
            # Excel konfigurieren
            excel_result = self.configure_excel(font_name, font_size_excel, target_path)
            if not excel_result["success"]:
                return excel_result
                
            # Outlook-Vorlagen kopieren
            outlook_result = self.copy_outlook_templates()
            if not outlook_result["success"]:
                self.logger.warning(f"Outlook-Konfiguration teilweise fehlgeschlagen: {outlook_result.get('error', '')}")
            
            return {
                "success": True,
                "message": "Office-Einstellungen erfolgreich konfiguriert",
                "applied_count": len(self.applied_settings),
                "word_start_screen_disabled": bool(word_result.get("word_start_screen_disabled", False)),
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Office-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_word(self, font_name="Aptos", font_size=11, target_path=""):
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
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Word-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_excel(self, font_name="Aptos", font_size=10, target_path=""):
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
            }
            
            # Schriftart-Einstellungen
            font_settings = {
                "Default Font": (font_name, "excel_default_font"),
                "Default Font Size": (font_size, "excel_default_font_size")
            }
            
            # Registry-Einstellungen anwenden
            self._apply_excel_registry_settings(excel_settings, font_settings)
            
            # Angewandte Einstellungen protokollieren
            self._log_applied_settings("Excel")
            
            return {"success": True, "message": "Excel erfolgreich konfiguriert"}
            
        except Exception as e:
            self.logger.error(f"Fehler bei Excel-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    

    def copy_outlook_templates(self):
        """Outlook-Vorlagen kopieren"""
        try:
            self.logger.info("Outlook-Vorlagen werden kopiert...")

            # Outlook-Benutzerverzeichnis finden
            outlook_templates_dir = self._get_outlook_templates_dir()
            if not outlook_templates_dir:
                return {"success": False, "error": "Outlook-Vorlagenverzeichnis nicht gefunden"}

            # Quell-Template-Datei aus Unterordner 'Sonstiges/Standards'
            import sys
            if getattr(sys, 'frozen', False):
                # Ausgeführt als EXE (PyInstaller)
                base_dir = Path(sys.executable).parent
            else:
                # Ausgeführt als Script
                base_dir = Path(__file__).parent.parent.parent

            source_template = base_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm"

            if source_template.exists():
                target_path = outlook_templates_dir / "NormalEmail.dotm"
                shutil.copy2(source_template, target_path)
                self.logger.info(f"Outlook-Vorlage kopiert: {target_path}")
                return {"success": True, "message": "Outlook-Vorlagen erfolgreich kopiert"}
            else:
                self.logger.warning(f"Quell-Template nicht gefunden: {source_template}")
                return {"success": False, "error": "Outlook-Vorlage nicht gefunden"}

        except Exception as e:
            self.logger.error(f"Fehler beim Kopieren der Outlook-Vorlagen: {e}")
            return {"success": False, "error": str(e)}
    
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
    
