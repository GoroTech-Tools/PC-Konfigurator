"""
Office-Konfiguration Module
===========================

Konfiguriert Office-Programme (Word, Excel) mit Schriftarten, Pfaden und anderen Einstellungen.
Portiert aus dem ursprünglichen PowerShell-Skript.
Jetzt mit detaillierten Registry-Erläuterungen.
"""

import winreg
import os
import subprocess
import time
import logging
import shutil
from pathlib import Path
import psutil
from registry_explainer import RegistryExplainer
import sys, os
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class OfficeConfigurator:
    """Klasse zur Konfiguration von Office-Programmen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry_explainer = RegistryExplainer()
        self.applied_settings = []  # Track applied settings for logging
        
    def initialize_office(self):
        """Office-Programme initialisieren (wie im PowerShell-Skript)"""
        try:
            self.logger.info("Initialisierung von Office-Programmen...")
            
            # Excel und Word starten und wieder beenden (für Registry-Initialisierung)
            programs = [("EXCEL.EXE", "Excel"), ("WINWORD.EXE", "Word")]
            
            for exe_name, program_name in programs:
                if not self._is_process_running(exe_name):
                    self.logger.info(f"{program_name} wird initialisiert...")
                    self._start_and_stop_program(exe_name)
                else:
                    self.logger.info(f"{program_name} läuft bereits")
            
            # OfficeClickToRun beenden (falls möglich)
            self._stop_office_clicktorun()
            
            return {"success": True, "message": "Office-Programme erfolgreich initialisiert"}
            
        except Exception as e:
            self.logger.error(f"Fehler bei Office-Initialisierung: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_all_settings(self, config):
        """Alle Office-Einstellungen konfigurieren"""
        try:
            self.logger.info("Konfiguration der Office-Einstellungen...")
            
            font_name = config.get("font_name", "Aptos")
            font_size_word = config.get("font_size_word", 11)
            font_size_excel = config.get("font_size_excel", 10)
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
            
            return {"success": True, "message": "Office-Einstellungen erfolgreich konfiguriert"}
            
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
                "DOC-PATH": (str(target_path) if target_path else self._get_default_docs_path(), "word_doc_path"),
                # Autokorrektur-Optionen:
                "CorrectCapsLock": (0, "word_correct_initial_caps"),
                "CorrectSentenceCaps": (0, "word_correct_sentence_caps"),
                "AutoFormatAsYouTypeApplyBulletedLists": (0, "word_auto_bullets"),
                "AutoFormatAsYouTypeApplyNumberedLists": (0, "word_auto_numbering")
            }
            
            # Schriftart-Einstellungen
            font_settings = {
                "Default Font": (font_name, "word_default_font"),
                "Default Font Size": (font_size, "word_default_font_size")
            }
            
            # Registry-Einstellungen anwenden
            self._apply_word_registry_settings(word_settings, font_settings)
            
            # Angewandte Einstellungen protokollieren
            self._log_applied_settings("Word")
            
            return {"success": True, "message": "Word erfolgreich konfiguriert"}
            
        except Exception as e:
            self.logger.error(f"Fehler bei Word-Konfiguration: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_excel(self, font_name="Aptos", font_size=10, target_path=""):
        """Excel-spezifische Einstellungen konfigurieren"""
        try:
            self.logger.info(f"Excel konfigurieren: Schriftart={font_name}, Größe={font_size}")
            
            # Excel Registry-Einstellungen mit Erläuterungen
            excel_settings = {
                "EXCEL-PATH": (str(target_path) if target_path else self._get_default_docs_path(), "excel_path")
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
    
    def _is_process_running(self, process_name):
        """Prüfen, ob ein Prozess läuft"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].upper() == process_name.upper():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def _start_and_stop_program(self, exe_name):
        """Programm starten und nach kurzer Zeit wieder beenden"""
        try:
            # Programm starten (minimiert)
            if exe_name == "EXCEL.EXE":
                process = subprocess.Popen(["excel"], shell=True)
            elif exe_name == "WINWORD.EXE":
                process = subprocess.Popen(["winword"], shell=True)
            else:
                return
                
            # 5 Sekunden warten
            time.sleep(5)
            
            # Programm beenden
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'].upper() == exe_name.upper():
                        proc.terminate()
                        proc.wait(timeout=10)
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Fehler beim Starten/Stoppen von {exe_name}: {e}")
    
    def _stop_office_clicktorun(self):
        """OfficeClickToRun-Prozess beenden"""
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'].upper() == "OFFICECLICKTORUN.EXE":
                        proc.terminate()
                        self.logger.info("OfficeClickToRun erfolgreich beendet")
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.warning(f"OfficeClickToRun konnte nicht beendet werden: {e}")
    
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
    
    def _set_registry_values(self, hive, key_path, values):
        """Registry-Werte setzen"""
        try:
            # Registry-Key öffnen oder erstellen
            try:
                with winreg.OpenKey(hive, key_path, 0, winreg.KEY_WRITE) as key:
                    for name, value in values.items():
                        if isinstance(value, int):
                            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                        else:
                            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
            except FileNotFoundError:
                # Key existiert nicht, erstellen
                with winreg.CreateKey(hive, key_path) as key:
                    for name, value in values.items():
                        if isinstance(value, int):
                            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                        else:
                            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
                            
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen der Registry-Werte für {key_path}: {e}")
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
    
    def get_office_installation_paths(self):
        """Office-Installationspfade ermitteln"""
        paths = {}
        
        try:
            # Registry nach Office-Pfaden durchsuchen
            registry_keys = [
                r"SOFTWARE\Microsoft\Office\16.0\Common\InstallRoot",
                r"SOFTWARE\Microsoft\Office\15.0\Common\InstallRoot",
                r"SOFTWARE\WOW6432Node\Microsoft\Office\16.0\Common\InstallRoot",
                r"SOFTWARE\WOW6432Node\Microsoft\Office\15.0\Common\InstallRoot"
            ]
            
            for key_path in registry_keys:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        install_path = winreg.QueryValueEx(key, "Path")[0]
                        if os.path.exists(install_path):
                            version = "16.0" if "16.0" in key_path else "15.0"
                            paths[version] = install_path
                except (FileNotFoundError, OSError):
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Fehler beim Ermitteln der Office-Pfade: {e}")
            
    def _log_applied_settings(self, program):
        """Zusammenfassung der angewandten Einstellungen protokollieren"""
        program_settings = [s for s in self.applied_settings if s["program"] == program]
        
        if program_settings:
            self.logger.info(f"=== {program} Konfiguration Zusammenfassung ===")
            for setting in program_settings:
                self.logger.info(f"✓ {setting['name']}: {setting['value']} ({setting['category']})")
            self.logger.info(f"=== {len(program_settings)} {program} Einstellungen angewendet ===")
    
    def get_applied_settings_summary(self):
        """Zusammenfassung aller angewandten Einstellungen für GUI"""
        summary = {
            "total_settings": len(self.applied_settings),
            "by_program": {},
            "by_category": {},
            "settings": self.applied_settings
        }
        
        for setting in self.applied_settings:
            program = setting["program"]
            category = setting["category"]
            
            if program not in summary["by_program"]:
                summary["by_program"][program] = 0
            summary["by_program"][program] += 1
            
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1
        
        return summary
    
    def get_registry_documentation(self):
        """Vollständige Registry-Dokumentation für Export"""
        return self.registry_explainer.export_all_settings()
    
    def apply_custom_registry_settings(self, active_settings):
        """Wendet nur die vom Benutzer aktivierten Registry-Einstellungen an"""
        try:
            self.logger.info("Starte benutzerdefinierte Registry-Konfiguration...")
            
            # Word-Einstellungen anwenden
            if any(key.startswith("word_") and active_settings.get(key, False) for key in active_settings):
                self._configure_word_with_custom_settings(active_settings)
            
            # Excel-Einstellungen anwenden  
            if any(key.startswith("excel_") and active_settings.get(key, False) for key in active_settings):
                self._configure_excel_with_custom_settings(active_settings)
            
            # Office-Schriftart-Einstellungen anwenden
            if any(key.startswith("office_") and active_settings.get(key, False) for key in active_settings):
                self._configure_office_fonts_with_custom_settings(active_settings)
            
            # Windows-System-Einstellungen anwenden
            if any(key.startswith("windows_") and active_settings.get(key, False) for key in active_settings):
                self._configure_windows_system_settings(active_settings)
            
            return {"success": True, "message": "Benutzerdefinierte Einstellungen erfolgreich angewendet"}
            
        except Exception as e:
            self.logger.error(f"Fehler bei benutzerdefinierten Einstellungen: {e}")
            return {"success": False, "message": f"Fehler: {e}"}
    
    def _configure_word_with_custom_settings(self, settings):
        """Konfiguriert Word mit benutzerdefinierten Einstellungen"""
        word_versions = self._get_office_versions("Word")
        
        for version in word_versions:
            word_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options"
            
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, word_key_path) as key:
                    # Entwicklertools
                    if settings.get("word_developer_tab", False):
                        winreg.SetValueEx(key, "DeveloperTab", 0, winreg.REG_DWORD, 1)
                        self._track_setting("Word", version, "DeveloperTab", "1", "Entwicklertools aktiviert", "Benutzeroberfläche")
                    
                    # Lineal anzeigen
                    if settings.get("word_ruler_display", False):
                        winreg.SetValueEx(key, "ShowRuler", 0, winreg.REG_DWORD, 1)
                        self._track_setting("Word", version, "ShowRuler", "1", "Lineal standardmäßig anzeigen", "Benutzeroberfläche")
                    
                    # Formatierungszeichen
                    if settings.get("word_format_marks", False):
                        winreg.SetValueEx(key, "ShowFormattingMarks", 0, winreg.REG_DWORD, 1)
                        self._track_setting("Word", version, "ShowFormattingMarks", "1", "Formatierungszeichen anzeigen", "Formatierung")
                    
                    # Tabellenlinien
                    if settings.get("word_table_gridlines", False):
                        winreg.SetValueEx(key, "ShowTableGridlines", 0, winreg.REG_DWORD, 1)
                        self._track_setting("Word", version, "ShowTableGridlines", "1", "Tabellenlinien anzeigen", "Formatierung")
                
            except Exception as e:
                self.logger.error(f"Fehler bei Word-{version} Konfiguration: {e}")
    
    def _configure_excel_with_custom_settings(self, settings):
        """Konfiguriert Excel mit benutzerdefinierten Einstellungen"""
        excel_versions = self._get_office_versions("Excel")
        
        for version in excel_versions:
            excel_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options"
            
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, excel_key_path) as key:
                    # Entwicklertools
                    if settings.get("excel_developer_tab", False):
                        winreg.SetValueEx(key, "DeveloperTab", 0, winreg.REG_DWORD, 1)
                        self._track_setting("Excel", version, "DeveloperTab", "1", "Entwicklertools aktiviert", "Benutzeroberfläche")
                    
                    # Bearbeitungsleiste erweitert
                    if settings.get("excel_formula_bar", False):
                        winreg.SetValueEx(key, "FormulaBarHeight", 0, winreg.REG_DWORD, 3)
                        self._track_setting("Excel", version, "FormulaBarHeight", "3", "Erweiterte Bearbeitungsleiste", "Benutzeroberfläche")
                    
                    # Gitternetzlinien
                    if settings.get("excel_gridlines", False):
                        winreg.SetValueEx(key, "ShowGridlines", 0, winreg.REG_DWORD, 1)
                        self._track_setting("Excel", version, "ShowGridlines", "1", "Gitternetzlinien anzeigen", "Benutzeroberfläche")
                
            except Exception as e:
                self.logger.error(f"Fehler bei Excel-{version} Konfiguration: {e}")
    
    def _configure_office_fonts_with_custom_settings(self, settings):
        """Konfiguriert Office-Schriftarten mit benutzerdefinierten Einstellungen"""
        if not settings.get("office_default_font", False):
            return
            
        try:
            # Hole bevorzugte Schriftart aus der Haupt-GUI
            selected_font = getattr(self, 'selected_font', 'Aptos')
            
            word_versions = self._get_office_versions("Word")
            excel_versions = self._get_office_versions("Excel")
            
            # Word-Standardschriftart setzen
            for version in word_versions:
                word_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options"
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, word_key_path) as key:
                        winreg.SetValueEx(key, "DefaultFont", 0, winreg.REG_SZ, selected_font)
                        self._track_setting("Word", version, "DefaultFont", selected_font, f"Standardschriftart auf {selected_font} gesetzt", "Schriftarten")
                except Exception as e:
                    self.logger.error(f"Fehler bei Word-{version} Schriftart-Konfiguration: {e}")
            
            # Excel-Standardschriftart setzen  
            for version in excel_versions:
                excel_key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options"
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, excel_key_path) as key:
                        winreg.SetValueEx(key, "DefaultFont", 0, winreg.REG_SZ, selected_font)
                        self._track_setting("Excel", version, "DefaultFont", selected_font, f"Standardschriftart auf {selected_font} gesetzt", "Schriftarten")
                except Exception as e:
                    self.logger.error(f"Fehler bei Excel-{version} Schriftart-Konfiguration: {e}")
                        
        except Exception as e:
            self.logger.error(f"Fehler bei Office-Schriftart-Konfiguration: {e}")
    
    def _configure_windows_system_settings(self, settings):
        """Konfiguriert Windows-System-Einstellungen (Taskleiste, Kontextmenü)"""
        try:
            self.logger.info("Konfiguriere Windows-System-Einstellungen...")
            
            # Taskleiste linksbündig ausrichten (Windows 11)
            if settings.get("windows_taskbar_left_align", False):
                self._set_taskbar_alignment_left()
            
            # Klassisches Kontextmenü aktivieren (Windows 11)
            if settings.get("windows_context_menu_classic", False):
                self._enable_classic_context_menu()
                
            # Suchfeld in Taskleiste ausblenden
            if settings.get("windows_taskbar_search_hide", False):
                self._hide_taskbar_search()
                
            # Widgets in Taskleiste ausblenden
            if settings.get("windows_taskbar_widgets_hide", False):
                self._hide_taskbar_widgets()
            
            # Explorer neu starten um Änderungen zu übernehmen
            self._restart_explorer()
            
        except Exception as e:
            self.logger.error(f"Fehler bei Windows-System-Konfiguration: {e}")
    
    def _set_taskbar_alignment_left(self):
        """Taskleiste linksbündig ausrichten (Windows 11)"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # TaskbarAl = 0 für linksbündig, 1 für zentriert
                winreg.SetValueEx(key, "TaskbarAl", 0, winreg.REG_DWORD, 0)
                self._track_setting("Windows", "System", "TaskbarAl", "0", 
                                  "Taskleiste linksbündig ausgerichtet", "System")
                self.logger.info("Taskleiste wurde auf linksbündige Ausrichtung eingestellt")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen der Taskleisten-Ausrichtung: {e}")
    
    def _enable_classic_context_menu(self):
        """Klassisches Kontextmenü aktivieren (Windows 11)"""
        try:
            # Registry-Schlüssel für klassisches Kontextmenü
            key_path = r"SOFTWARE\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # Leerer String aktiviert klassisches Kontextmenü
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
                self._track_setting("Windows", "System", "ClassicContextMenu", "aktiviert", 
                                  "Klassisches Kontextmenü aktiviert", "System")
                self.logger.info("Klassisches Kontextmenü wurde aktiviert")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Aktivieren des klassischen Kontextmenüs: {e}")
    
    def _hide_taskbar_search(self):
        """Suchfeld in Taskleiste ausblenden"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # SearchboxTaskbarMode = 0 für ausgeblendet, 1 für Icon, 2 für Feld
                winreg.SetValueEx(key, "SearchboxTaskbarMode", 0, winreg.REG_DWORD, 0)
                self._track_setting("Windows", "System", "SearchboxTaskbarMode", "0", 
                                  "Taskleisten-Suchfeld ausgeblendet", "System")
                self.logger.info("Taskleisten-Suchfeld wurde ausgeblendet")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Ausblenden des Suchfelds: {e}")
    
    def _hide_taskbar_widgets(self):
        """Widgets in Taskleiste ausblenden"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # TaskbarDa = 0 für ausgeblendet, 1 für angezeigt
                winreg.SetValueEx(key, "TaskbarDa", 0, winreg.REG_DWORD, 0)
                self._track_setting("Windows", "System", "TaskbarDa", "0", 
                                  "Taskleisten-Widgets ausgeblendet", "System")
                self.logger.info("Taskleisten-Widgets wurden ausgeblendet")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Ausblenden der Widgets: {e}")
    
    def _restart_explorer(self):
        """Windows Explorer neu starten um Registry-Änderungen zu übernehmen"""
        try:
            self.logger.info("Starte Windows Explorer neu...")
            
            # Explorer beenden
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], 
                         capture_output=True, check=False)
            
            # Kurz warten
            time.sleep(2)
            
            # Explorer wieder starten
            subprocess.Popen(["explorer.exe"])
            
            self.logger.info("Windows Explorer wurde neugestartet")
            
        except Exception as e:
            self.logger.warning(f"Explorer-Neustart fehlgeschlagen: {e}")
    
    def _get_office_versions(self, program):
        """Ermittelt verfügbare Office-Versionen für ein Programm"""
        versions = []
        office_versions = ["16.0", "15.0"]  # Office 2016/2019/2021 und Office 2013
        
        for version in office_versions:
            try:
                key_path = f"SOFTWARE\\Microsoft\\Office\\{version}\\{program}\\Options"
                # Versuche den Key zu öffnen
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ):
                    versions.append(version)
            except (FileNotFoundError, OSError):
                # Version nicht installiert oder Key existiert nicht
                continue
                
        # Falls keine Version gefunden, füge Standard-Versionen hinzu (werden bei Bedarf erstellt)
        if not versions:
            versions = ["16.0"]  # Standardmäßig neueste Version
            
        return versions
    
    def _track_setting(self, program, version, name, value, description, category):
        """Verfolge angewandte Einstellung für Logging"""
        self.applied_settings.append({
            "program": program,
            "version": version,
            "key_path": "",
            "name": name,
            "value": value,
            "description": description,
            "impact": description,
            "category": category
        })