"""
Template Recovery and Safe Font Configuration
============================================

Sichere Wiederherstellung von beschädigten Office-Templates
und Registry-basierte Schriftart-Konfiguration
"""

import os
import shutil
from pathlib import Path
import logging
import winreg


class SafeOfficeConfigurator:
    """Sichere Office-Konfiguration ohne Template-Manipulation"""
    
    def __init__(self, app_dir):
        """
        Initialisiert den sicheren Office-Konfigurator
        
        Args:
            app_dir: Verzeichnis der Anwendung
        """
        self.app_dir = Path(app_dir)
        self.logger = logging.getLogger(__name__)
        
        # Template-Pfade
        self.source_templates = {
            'normal_dotm': self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Normal.dotm",
            'mappe_xltx': self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Mappe.xltx",
            'normal_email_dotm': self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm"
        }
        
        # Benutzer Template-Pfade
        self.target_paths = {
            'normal_dotm': Path(os.environ['APPDATA']) / "Microsoft" / "Templates" / "Normal.dotm",
            'mappe_xltx': Path(os.environ['APPDATA']) / "Microsoft" / "Excel" / "XLSTART" / "Mappe.xltx",
            'normal_email_dotm': Path(os.environ['APPDATA']) / "Microsoft" / "Templates" / "NormalEmail.dotm"
        }
    
    def recover_damaged_templates(self):
        """
        Stellt beschädigte Templates wieder her durch Kopieren der Original-Templates
        """
        results = {}
        
        for template_key, source_path in self.source_templates.items():
            target_path = self.target_paths[template_key]
            
            try:
                if not source_path.exists():
                    self.logger.warning(f"Quelldatei nicht gefunden: {source_path}")
                    results[template_key] = False
                    continue
                
                # Backup des beschädigten Templates erstellen
                if target_path.exists():
                    backup_path = target_path.with_suffix(f'{target_path.suffix}.damaged_backup')
                    shutil.copy2(target_path, backup_path)
                    self.logger.info(f"Beschädigtes Template gesichert: {backup_path}")
                
                # Zielverzeichnis erstellen falls nicht vorhanden
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Originales, unveränderte Template kopieren
                shutil.copy2(source_path, target_path)
                self.logger.info(f"Original-Template wiederhergestellt: {target_path}")
                results[template_key] = True
                
            except Exception as e:
                self.logger.error(f"Fehler bei Template-Wiederherstellung {template_key}: {str(e)}")
                results[template_key] = False
        
        return results
    
    def configure_fonts_via_registry(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        Konfiguriert Schriftarten über Registry-Einstellungen (sicherer Ansatz)
        """
        results = {}
        
        try:
            # Word-Schriftart-Einstellungen
            word_results = self._configure_word_font_registry(font_name, font_size_word)
            results['word'] = word_results
            
            # Excel-Schriftart-Einstellungen  
            excel_results = self._configure_excel_font_registry(font_name, font_size_excel)
            results['excel'] = excel_results
            
            # Outlook-Schriftart-Einstellungen
            outlook_results = self._configure_outlook_font_registry(font_name, font_size_word)
            results['outlook'] = outlook_results
            
        except Exception as e:
            self.logger.error(f"Fehler bei Registry-Schriftart-Konfiguration: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _configure_word_font_registry(self, font_name, font_size):
        """Konfiguriert Word-Schriftarten über Registry"""
        try:
            # Word-Registry-Schlüssel für Standard-Schriftart
            word_versions = ['16.0', '15.0', '14.0']  # Office 2016+, 2013, 2010
            
            for version in word_versions:
                try:
                    key_path = f"Software\\Microsoft\\Office\\{version}\\Word\\Options"
                    
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        # Standard-Schriftart setzen
                        winreg.SetValueEx(key, "DefaultFont", 0, winreg.REG_SZ, font_name)
                        # Standard-Schriftgröße setzen
                        winreg.SetValueEx(key, "DefaultFontSize", 0, winreg.REG_DWORD, font_size)
                        
                        self.logger.info(f"Word {version} Schriftart konfiguriert: {font_name} {font_size}pt")
                        
                except Exception as e:
                    self.logger.warning(f"Konnte Word {version} nicht konfigurieren: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Word-Registry-Konfiguration: {e}")
            return False
    
    def _configure_excel_font_registry(self, font_name, font_size):
        """Konfiguriert Excel-Schriftarten über Registry"""
        try:
            excel_versions = ['16.0', '15.0', '14.0']
            
            for version in excel_versions:
                try:
                    key_path = f"Software\\Microsoft\\Office\\{version}\\Excel\\Options"
                    
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        # Standard-Schriftart setzen
                        winreg.SetValueEx(key, "DefaultFont", 0, winreg.REG_SZ, font_name)
                        # Standard-Schriftgröße setzen  
                        winreg.SetValueEx(key, "DefaultFontSize", 0, winreg.REG_DWORD, font_size)
                        
                        self.logger.info(f"Excel {version} Schriftart konfiguriert: {font_name} {font_size}pt")
                        
                except Exception as e:
                    self.logger.warning(f"Konnte Excel {version} nicht konfigurieren: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Excel-Registry-Konfiguration: {e}")
            return False
    
    def _configure_outlook_font_registry(self, font_name, font_size=11):
        """Konfiguriert Outlook-Schriftarten über Registry"""
        try:
            outlook_versions = ['16.0', '15.0', '14.0']
            
            for version in outlook_versions:
                try:
                    key_path = f"Software\\Microsoft\\Office\\{version}\\Outlook\\Options"
                    
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        # Neue E-Mail-Schriftart setzen (tatsächlich von Outlook verwendete Keys)
                        winreg.SetValueEx(key, "NewMailFont", 0, winreg.REG_SZ, font_name)
                        winreg.SetValueEx(key, "NewMailFontSize", 0, winreg.REG_DWORD, int(font_size))
                        winreg.SetValueEx(key, "ReplyForwardFont", 0, winreg.REG_SZ, font_name)
                        winreg.SetValueEx(key, "ReplyForwardFontSize", 0, winreg.REG_DWORD, int(font_size))
                        # Älterer Key (Kompatibilität)
                        winreg.SetValueEx(key, "DefaultMailFont", 0, winreg.REG_SZ, font_name)

                        self.logger.info(f"Outlook {version} Schriftart konfiguriert: {font_name} {font_size}pt (NewMail + ReplyForward)")
                        
                except Exception as e:
                    self.logger.warning(f"Konnte Outlook {version} nicht konfigurieren: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Outlook-Registry-Konfiguration: {e}")
            return False
    
    def check_template_status(self):
        """Überprüft den Status der Office-Templates"""
        status = {}
        
        for template_key, target_path in self.target_paths.items():
            if target_path.exists():
                try:
                    # Einfacher Dateigrößen-Check als Indikator für Beschädigung
                    size = target_path.stat().st_size
                    
                    # Minimum-Größen für gültige Templates
                    min_sizes = {
                        'normal_dotm': 10000,      # Mindestens 10KB
                        'mappe_xltx': 5000,        # Mindestens 5KB  
                        'normal_email_dotm': 8000  # Mindestens 8KB
                    }
                    
                    min_size = min_sizes.get(template_key, 1000)
                    
                    if size >= min_size:
                        status[template_key] = "OK"
                    else:
                        status[template_key] = "Beschädigt (zu klein)"
                        
                except Exception as e:
                    status[template_key] = f"Fehler: {str(e)}"
            else:
                status[template_key] = "Nicht vorhanden"
        
        return status
    
    def safe_font_setup(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        Komplette sichere Schriftart-Konfiguration:
        1. Templates wiederherstellen falls beschädigt
        2. Registry-basierte Schriftart-Konfiguration
        """
        results = {
            'template_recovery': {},
            'font_configuration': {},
            'success': False
        }
        
        # 1. Template-Status prüfen
        template_status = self.check_template_status()
        damaged_templates = [k for k, v in template_status.items() if "Beschädigt" in v or "Fehler" in v]
        
        # 2. Beschädigte Templates wiederherstellen
        if damaged_templates:
            self.logger.info(f"Beschädigte Templates erkannt: {damaged_templates}")
            recovery_results = self.recover_damaged_templates()
            results['template_recovery'] = recovery_results
        else:
            results['template_recovery'] = {k: True for k in self.target_paths.keys()}
        
        # 3. Registry-basierte Schriftart-Konfiguration
        font_results = self.configure_fonts_via_registry(font_name, font_size_word, font_size_excel)
        results['font_configuration'] = font_results
        
        # 4. Gesamtergebnis bewerten
        recovery_success = all(results['template_recovery'].values())
        font_success = all(v for k, v in font_results.items() if k != 'error')
        
        results['success'] = recovery_success and font_success
        
        return results
    
    def configure_safe_office_defaults(self, font_name="Aptos", font_size_word=11, font_size_excel=10):
        """
        Sichere Office-Standardkonfiguration mit Schriftart-Einstellungen
        
        Args:
            font_name: Name der zu setzenden Schriftart (Standard: Aptos)
            font_size_word: Schriftgröße für Word (Standard: 11)
            font_size_excel: Schriftgröße für Excel (Standard: 10)
            
        Returns:
            dict: Ergebnisse der Konfiguration
        """
        self.logger.info(f"🔧 Konfiguriere Office mit {font_name} (Word: {font_size_word}pt, Excel: {font_size_excel}pt)")
        
        results = {
            'template_status': {},
            'font_configuration': {},
            'template_recovery': {},
            'success': False
        }
        
        try:
            # 1. Template-Status prüfen
            template_status = self.check_template_status()
            results['template_status'] = template_status
            damaged_templates = [k for k, v in template_status.items() if "Beschädigt" in v or "Fehler" in v]
            
            # 2. Beschädigte Templates wiederherstellen falls nötig
            if damaged_templates:
                self.logger.info(f"Beschädigte Templates erkannt: {damaged_templates}")
                recovery_results = self.recover_damaged_templates()
                results['template_recovery'] = recovery_results
            else:
                results['template_recovery'] = {k: True for k in self.target_paths.keys()}
            
            # 3. Registry-basierte Schriftart-Konfiguration
            font_results = self.configure_fonts_via_registry(font_name, font_size_word, font_size_excel)
            results['font_configuration'] = font_results
            
            # 4. Gesamtergebnis bewerten
            recovery_success = all(results['template_recovery'].values())
            font_success = all(v for k, v in font_results.items() if k != 'error')
            
            results['success'] = recovery_success and font_success
            
            if results['success']:
                self.logger.info("✅ Office-Konfiguration erfolgreich abgeschlossen")
            else:
                self.logger.warning("⚠️ Office-Konfiguration teilweise fehlgeschlagen")
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Office-Konfiguration: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        return results