#!/usr/bin/env python3
"""
Template-Preprocessor für Office-Vorlagen - KORRUPTIGUNGSFREIE VERSION
Verarbeitet Templates OHNE die Originale zu verändern
"""

import os
import shutil
import time
from pathlib import Path
from safe_template_processor import SafeTemplateProcessor


class TemplatePreprocessor:
    def __init__(self, app_dir):
        """
        Initialisiert den Template-Preprocessor
        
        Args:
            app_dir: Hauptverzeichnis der Anwendung
        """
        self.app_dir = Path(app_dir)
        
        # Logger setup
        import logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Quellverzeichnis für Templates (NIEMALS BEARBEITEN!)
        self.source_dir = self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards"
        
        # Template-Pfade im Quellverzeichnis (READ-ONLY!)
        self.source_normal_dotm = self.source_dir / "Normal.dotm"
        self.source_mappe_xltx = self.source_dir / "Mappe.xltx"
        self.source_normal_email_dotm = self.source_dir / "NormalEmail.dotm"
        
        # Benutzer-Zielverzeichnisse
        self.user_templates_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Templates"
        self.user_excel_startup_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Excel" / "XLSTART"
        
        # Benutzerspezifische Template-Pfade
        self.user_normal_dotm = self.user_templates_dir / "Normal.dotm"
        self.user_mappe_xltx = self.user_excel_startup_dir / "Mappe.xltx"
        self.user_normal_email_dotm = self.user_templates_dir / "NormalEmail.dotm"
        
        # Temporäres Verzeichnis für bearbeitete Templates
        self.temp_dir = Path.home() / "AppData" / "Local" / "Temp" / "PC-Konfigurator-Templates"
        
        # Pfade für bearbeitete Templates (werden zur Laufzeit gesetzt)
        self.processed_normal_dotm = None
        self.processed_mappe_xltx = None
        self.processed_normal_email_dotm = None
        
        # SafeTemplateProcessor für sichere Template-Bearbeitung
        self.safe_processor = SafeTemplateProcessor()
        
        self.logger.info(f"TemplatePreprocessor initialisiert - Quellverzeichnis: {self.source_dir} (READ-ONLY)")

    def create_customized_templates(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        Erstellt angepasste Kopien der Original-Templates (OHNE Originale zu verändern!)
        
        Args:
            font_name: Gewünschte Schriftart
            font_size_word: Schriftgröße für Word-Templates
            font_size_excel: Schriftgröße für Excel-Templates
            
        Returns:
            dict: Erfolgsstatus für jedes Template
        """
        self.logger.info(f"Erstelle angepasste Template-Kopien mit {font_name} (Word: {font_size_word}pt, Excel: {font_size_excel}pt)")
        
        results = {
            'normal_dotm': False,
            'mappe_xltx': False,
            'normal_email_dotm': False
        }
        
        # Temporäres Verzeichnis erstellen/bereinigen
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Template-Definitionen
        templates = {
            'normal_dotm': (self.source_normal_dotm, 'word', 'Normal.dotm'),
            'mappe_xltx': (self.source_mappe_xltx, 'excel', 'Mappe.xltx'),
            'normal_email_dotm': (self.source_normal_email_dotm, 'word', 'NormalEmail.dotm')
        }
        
        for template_key, (source_path, template_type, filename) in templates.items():
            if source_path.exists():
                try:
                    # 1. Erstelle Arbeitskopie im temporären Verzeichnis
                    temp_template = self.temp_dir / filename
                    shutil.copy2(source_path, temp_template)
                    self.logger.info(f"Arbeitskopie erstellt: {filename} -> TEMP (Original UNVERÄNDERT)")
                    
                    # 2. Bearbeite die Arbeitskopie (NIEMALS das Original!)
                    if template_type == 'word':
                        success = self.safe_processor.update_word_template_safely(
                            temp_template, font_name, font_size_word
                        )
                    elif template_type == 'excel':
                        success = self.safe_processor.update_excel_template_safely(
                            temp_template, font_name, font_size_excel
                        )
                    
                    if success:
                        # Bearbeitete Kopie für Deployment merken
                        setattr(self, f"processed_{template_key}", temp_template)
                        self.logger.info(f"Template-Kopie erfolgreich angepasst: {filename}")
                        
                        # SOFORT KOPIEREN um Timing-Probleme zu vermeiden
                        immediate_success = self._immediate_copy_template(template_key, temp_template)
                        
                        # Merken, dass sofort kopiert wurde (für späteren Skip)
                        setattr(self, f"immediate_copied_{template_key}", immediate_success)
                        
                    else:
                        self.logger.error(f"Fehler beim Anpassen der Template-Kopie: {filename}")
                    
                    results[template_key] = success
                    
                except Exception as e:
                    self.logger.error(f"Ausnahme beim Verarbeiten von {filename}: {e}")
                    results[template_key] = False
            else:
                self.logger.warning(f"Original-Template nicht gefunden: {source_path}")
                results[template_key] = False
        
        return results

    def _immediate_copy_template(self, template_key, temp_template_path):
        """
        Kopiert ein bearbeitetes Template sofort an die richtige Stelle
        """
        target_mapping = {
            'normal_dotm': self.user_normal_dotm,
            'mappe_xltx': self.user_mappe_xltx,
            'normal_email_dotm': self.user_normal_email_dotm
        }
        
        target_path = target_mapping.get(template_key)
        if not target_path:
            self.logger.error(f"Unbekannter Template-Key: {template_key}")
            return False
            
        try:
            # Zielverzeichnis erstellen falls nötig
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Template sofort kopieren
            import shutil
            shutil.copy2(temp_template_path, target_path)
            self.logger.info(f"⚡ Template SOFORT kopiert: {temp_template_path.name} -> {target_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim sofortigen Kopieren von {template_key}: {e}")
            return False
    
    def copy_templates_to_user_directories(self):
        """
        Kopiert die bearbeiteten Template-Kopien in die Benutzerverzeichnisse
        
        Returns:
            dict: Erfolgsstatus für jedes kopierte Template
        """
        self.logger.info("Kopiere bearbeitete Template-Kopien in Benutzerverzeichnisse")
        
        results = {
            'normal_dotm': False,
            'mappe_xltx': False,
            'normal_email_dotm': False
        }
        
        # Template-Zuordnungen: (bearbeitete_kopie, ziel_pfad)
        copy_mappings = {
            'normal_dotm': (self.processed_normal_dotm, self.user_normal_dotm),
            'mappe_xltx': (self.processed_mappe_xltx, self.user_mappe_xltx),
            'normal_email_dotm': (self.processed_normal_email_dotm, self.user_normal_email_dotm)
        }
        
        for template_key, (processed_path, target_path) in copy_mappings.items():
            # Prüfen ob bereits sofort kopiert wurde
            immediate_copied_attr = f"immediate_copied_{template_key}"
            if hasattr(self, immediate_copied_attr) and getattr(self, immediate_copied_attr):
                self.logger.info(f"⏩ Template bereits sofort kopiert, überspringe: {template_key}")
                results[template_key] = True
                continue
                
            if processed_path and processed_path.exists():
                try:
                    # Zielverzeichnis erstellen falls nötig
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Bearbeitete Template-Kopie in Benutzerverzeichnis kopieren
                    shutil.copy2(processed_path, target_path)
                    self.logger.info(f"Bearbeitetes Template kopiert: {processed_path.name} -> {target_path}")
                    
                    results[template_key] = True
                    
                except Exception as e:
                    self.logger.error(f"Fehler beim Kopieren von {processed_path.name if processed_path else template_key}: {e}")
                    results[template_key] = False
            else:
                self.logger.warning(f"Bearbeitetes Template nicht verfügbar: {template_key}")
                results[template_key] = False
        
        return results

    def process_and_deploy_templates(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        KORRUPTIONSFREIER Workflow: Template-Kopien anpassen und in Benutzerverzeichnisse kopieren
        
        Args:
            font_name: Gewünschte Schriftart
            font_size_word: Schriftgröße für Word-Templates
            font_size_excel: Schriftgröße für Excel-Templates
            
        Returns:
            dict: Gesamtergebnis der Template-Verarbeitung
        """
        self.logger.info(f"Starte KORRUPTIONSFREIE Template-Verarbeitung: {font_name} (Word: {font_size_word}pt, Excel: {font_size_excel}pt)")
        
        # 1. Templates als Kopien anpassen (Originale bleiben unverändert!)
        customization_results = self.create_customized_templates(font_name, font_size_word, font_size_excel)
        
        # Warten auf vollständigen COM-Cleanup (Office-Prozesse beenden)
        import time
        self.logger.info("Warte auf vollständigen COM-Cleanup...")
        time.sleep(3)  # 3 Sekunden warten für Office-Prozessbeendigung
        
        # 2. Angepasste Kopien zu Benutzern kopieren  
        deployment_results = self.copy_templates_to_user_directories()
        
        # 3. Temporäre Dateien aufräumen
        self.cleanup_temp_templates()
        
        # Statistiken berechnen
        templates_processed = sum(1 for success in customization_results.values() if success)
        templates_copied = sum(1 for success in deployment_results.values() if success)
        overall_success = (templates_processed > 0 and templates_copied > 0)
        
        result = {
            'customization': customization_results,
            'deployment': deployment_results,
            'overall_success': overall_success
        }
        
        self.logger.info(f"KORRUPTIONSFREIE Template-Verarbeitung abgeschlossen: {templates_processed} angepasst, {templates_copied} kopiert")
        
        return result
        
    def cleanup_temp_templates(self):
        """
        Räumt temporäre Template-Kopien auf
        """
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.logger.info("Temporäre Template-Kopien aufgeräumt")
        except Exception as e:
            self.logger.warning(f"Warnung beim Aufräumen temporärer Templates: {e}")
        
    def get_template_status(self):
        """
        Prüft Status der Templates
        
        Returns:
            dict: Status-Information über alle Templates
        """
        status = {
            'source_templates': {},
            'user_templates': {}
        }
        
        # Quell-Templates prüfen (READ-ONLY)
        source_templates = {
            'normal_dotm': self.source_normal_dotm,
            'mappe_xltx': self.source_mappe_xltx, 
            'normal_email_dotm': self.source_normal_email_dotm
        }
        
        for key, path in source_templates.items():
            status['source_templates'][key] = {
                'exists': path.exists(),
                'path': str(path),
                'size': path.stat().st_size if path.exists() else 0
            }
        
        # Benutzer-Templates prüfen
        user_templates = {
            'normal_dotm': self.user_normal_dotm,
            'mappe_xltx': self.user_mappe_xltx,
            'normal_email_dotm': self.user_normal_email_dotm
        }
        
        for key, path in user_templates.items():
            status['user_templates'][key] = {
                'exists': path.exists(),
                'path': str(path),
                'size': path.stat().st_size if path.exists() else 0
            }
        
        return status
    
    # ===== KOMPATIBILITÄTSMETHODEN FÜR main.py =====
    
    def deploy_and_configure_templates(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        Kompatibilitätsmethode für main.py
        Führt Template-Anpassung und Deployment aus
        """
        try:
            self.logger.info("📄 Standards-Templates werden angepasst und kopiert...")
            result = self.process_and_deploy_templates(
                font_name=font_name, 
                font_size_word=font_size_word, 
                font_size_excel=font_size_excel
            )
            
            # Für main.py Kompatibilität: customization -> modification_phase, deployment -> copy_phase
            # Konvertiere True/False zu {'success': True/False} Format
            modification_phase = {}
            for key, value in result.get('customization', {}).items():
                modification_phase[key] = {'success': value}
                
            copy_phase = {}
            for key, value in result.get('deployment', {}).items():
                copy_phase[key] = {'success': value}
            
            return {
                'modification_phase': modification_phase,
                'copy_phase': copy_phase,
                'overall_success': result.get('overall_success', False)
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei deploy_and_configure_templates: {e}")
            return {
                'modification_phase': {
                    'normal_dotm': {'success': False},
                    'mappe_xltx': {'success': False}, 
                    'normal_email_dotm': {'success': False}
                },
                'copy_phase': {
                    'normal_dotm': {'success': False},
                    'mappe_xltx': {'success': False}, 
                    'normal_email_dotm': {'success': False}
                },
                'overall_success': False
            }
    
    def check_templates_exist(self):
        """
        Kompatibilitätsmethode für main.py
        Prüft ob Templates in Benutzerverzeichnissen existieren
        """
        try:
            status = self.get_template_status()
            return {
                'normal_dotm': status['user_templates']['normal_dotm']['exists'],
                'mappe_xltx': status['user_templates']['mappe_xltx']['exists'],
                'normal_email_dotm': status['user_templates']['normal_email_dotm']['exists']
            }
        except Exception as e:
            self.logger.error(f"Fehler bei check_templates_exist: {e}")
            return {'normal_dotm': False, 'mappe_xltx': False, 'normal_email_dotm': False}
    
    def get_current_fonts_in_templates(self):
        """
        Kompatibilitätsmethode für main.py
        Gibt aktuelle Schriftarten in Templates zurück (vereinfacht)
        """
        try:
            # Vereinfachte Rückgabe - echte COM-Analyse wäre zu aufwändig
            return {
                'normal_dotm': 'Unbekannt',
                'mappe_xltx': 'Unbekannt', 
                'normal_email_dotm': 'Unbekannt'
            }
        except Exception as e:
            self.logger.error(f"Fehler bei get_current_fonts_in_templates: {e}")
            return {'normal_dotm': 'Fehler', 'mappe_xltx': 'Fehler', 'normal_email_dotm': 'Fehler'}
    
    def copy_templates_to_user(self):
        """
        Kompatibilitätsmethode für main.py
        Kopiert nur Templates ohne Anpassung
        """
        try:
            return self.copy_templates_to_user_directories()
        except Exception as e:
            self.logger.error(f"Fehler bei copy_templates_to_user: {e}")
            return {
                'normal_dotm': False,
                'mappe_xltx': False,
                'normal_email_dotm': False
            }
    
    def update_font_in_templates(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        Kompatibilitätsmethode für main.py
        Aktualisiert Schriftarten in Templates
        """
        try:
            return self.create_customized_templates(
                font_name=font_name,
                font_size_word=font_size_word,
                font_size_excel=font_size_excel
            )
        except Exception as e:
            self.logger.error(f"Fehler bei update_font_in_templates: {e}")
            return {
                'normal_dotm': False,
                'mappe_xltx': False,
                'normal_email_dotm': False
            }