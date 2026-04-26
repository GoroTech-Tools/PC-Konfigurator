"""
Font Installer Module
====================

Installiert benutzerdefinierte Fonts für die PC-Konfigurator-Anwendung.
Basiert auf der ursprünglichen PowerShell-Implementierung.
"""

import os
import shutil
import logging
from pathlib import Path
import winreg
import ctypes
from ctypes import wintypes


class FontInstaller:
    """Klasse zur Installation von benutzerdefinierten Fonts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Windows Font API Funktionen
        self.gdi32 = ctypes.windll.gdi32
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
    def install_fonts_from_directory(self, fonts_directory):
        """
        Installiert alle Fonts aus dem angegebenen Verzeichnis
        
        Args:
            fonts_directory: Pfad zum Fonts-Verzeichnis
            
        Returns:
            dict: Status und Liste der installierten Fonts
        """
        try:
            fonts_dir = Path(fonts_directory)
            if not fonts_dir.exists():
                return {
                    "success": False, 
                    "error": f"Fonts-Verzeichnis nicht gefunden: {fonts_dir}"
                }
            
            installed_fonts = []
            failed_fonts = []
            
            # Rekursiv alle Font-Dateien finden
            font_extensions = ['.ttf', '.otf', '.woff', '.woff2']
            font_files = []
            
            for ext in font_extensions:
                font_files.extend(fonts_dir.rglob(f'*{ext}'))
            
            self.logger.info(f"Gefundene Font-Dateien: {len(font_files)}")
            
            for font_file in font_files:
                try:
                    success = self._install_single_font(font_file)
                    if success:
                        installed_fonts.append(font_file.name)
                        self.logger.info(f"Font installiert: {font_file.name}")
                    else:
                        failed_fonts.append(font_file.name)
                        self.logger.warning(f"Font-Installation fehlgeschlagen: {font_file.name}")
                        
                except Exception as e:
                    failed_fonts.append(font_file.name)
                    self.logger.error(f"Fehler bei Font-Installation {font_file.name}: {e}")
            
            # System über neue Fonts benachrichtigen
            self._refresh_font_cache()
            
            return {
                "success": True,
                "installed_fonts": installed_fonts,
                "failed_fonts": failed_fonts,
                "total_processed": len(font_files)
            }
            
        except Exception as e:
            self.logger.error(f"Allgemeiner Fehler bei Font-Installation: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_single_font(self, font_file):
        """
        Installiert eine einzelne Font-Datei ausschließlich ins benutzerspezifische Verzeichnis
        
        Args:
            font_file: Path zur Font-Datei
        Returns:
            bool: True wenn erfolgreich installiert
        """
        try:
            # Ziel-Verzeichnis für User-Fonts
            fonts_user_dir = Path(os.environ['LOCALAPPDATA']) / 'Microsoft' / 'Windows' / 'Fonts'
            fonts_user_dir.mkdir(parents=True, exist_ok=True)

            # Font-Name aus Datei extrahieren
            font_name = self._get_font_name_from_file(font_file)
            if not font_name:
                font_name = font_file.stem

            # Font-Datei ins User-Verzeichnis kopieren
            target_file = fonts_user_dir / font_file.name

            # Prüfen ob Font bereits installiert ist
            if target_file.exists():
                self.logger.info(f"Font bereits installiert: {font_file.name}")
                return True

            # Font-Datei kopieren
            shutil.copy2(font_file, target_file)

            # Font in der Registry registrieren (nur für aktuellen Benutzer)
            registry_success = self._register_font_in_user_registry(font_name, font_file.name)

            # Font im System registrieren (nur für aktuelle Session)
            api_success = self._register_font_with_api(str(target_file))

            return registry_success and api_success

        except Exception as e:
            self.logger.error(f"Fehler bei Installation von {font_file.name}: {e}")
            return False
    
    def _get_font_name_from_file(self, font_file):
        """
        Versucht den Font-Namen aus der Font-Datei zu extrahieren
        
        Args:
            font_file: Path zur Font-Datei
            
        Returns:
            str: Font-Name oder None
        """
        try:
            # Vereinfachte Font-Name-Extraktion
            # Für vollständige Implementierung würde man Font-Parser benötigen
            name = font_file.stem
            
            # Grundlegende Bereinigung
            name = name.replace('-', ' ').replace('_', ' ')
            
            # Bekannte Font-Suffixe handhaben
            suffixes = ['Regular', 'Bold', 'Italic', 'Light', 'Medium', 'Thin', 'Black']
            for suffix in suffixes:
                if name.endswith(suffix):
                    name = f"{name[:-len(suffix)].strip()} ({suffix})"
                    break
            
            return name
            
        except Exception as e:
            self.logger.error(f"Fehler bei Font-Name-Extraktion für {font_file}: {e}")
            return None
    
    def _register_font_in_user_registry(self, font_name, font_filename):
        """
        Registriert Font in der User Registry (wenn keine Admin-Rechte)
        
        Args:
            font_name: Anzeigename des Fonts
            font_filename: Dateiname der Font-Datei
            
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            # User-Registry für Fonts
            key_path = r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, font_filename)
                self.logger.info(f"Font in User-Registry registriert: {font_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"User-Registry-Registrierung fehlgeschlagen: {e}")
            return False
    
    def _register_font_with_api(self, font_file_path):
        """
        Registriert Font über Windows API
        
        Args:
            font_file_path: Vollständiger Pfad zur Font-Datei
            
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            # AddFontResourceEx API aufrufen
            result = self.gdi32.AddFontResourceExW(
                ctypes.c_wchar_p(font_file_path),
                0x10,  # FR_PRIVATE
                None
            )
            
            if result > 0:
                self.logger.info(f"Font über API registriert: {font_file_path}")
                return True
            else:
                self.logger.warning(f"API-Registrierung fehlgeschlagen für: {font_file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Fehler bei API-Registrierung für {font_file_path}: {e}")
            return False
    
    def _refresh_font_cache(self):
        """
        Aktualisiert den System-Font-Cache
        """
        try:
            # System über Font-Änderungen benachrichtigen
            HWND_BROADCAST = 0xFFFF
            WM_FONTCHANGE = 0x001D
            
            self.user32.SendMessageW(
                HWND_BROADCAST,
                WM_FONTCHANGE,
                0,
                0
            )
            
            self.logger.info("Font-Cache erfolgreich aktualisiert")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren des Font-Cache: {e}")
