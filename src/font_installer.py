"""
Font Installer Module
====================

Installiert benutzerdefinierte Fonts für die PC-Konfigurator-Anwendung.
Basiert auf der ursprünglichen PowerShell-Implementierung.
"""

import os
import shutil
import logging
import re
from pathlib import Path
import winreg
import ctypes
from ctypes import wintypes


class FontInstaller:
    """Klasse zur Installation von benutzerdefinierten Fonts"""

    FONT_EXTENSIONS = ('.ttf', '.otf', '.woff', '.woff2')
    STYLE_TOKENS = {
        'regular', 'italic', 'bold', 'light', 'medium', 'thin', 'black',
        'semibold', 'semi', 'extrabold', 'extra', 'book', 'demi', 'heavy',
        'oblique', 'ultralight', 'extralight', 'solid'
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Windows Font API Funktionen
        self.gdi32 = ctypes.windll.gdi32
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

    def get_user_fonts_dir(self):
        """Liefert das benutzerspezifische Fonts-Verzeichnis."""
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return Path(local_app_data) / 'Microsoft' / 'Windows' / 'Fonts'

        # Fallback für Sonderkonstellationen (z. B. eingeschränkte Laufzeitkontexte):
        # Windows-Profile liegen üblicherweise unter %USERPROFILE%\AppData\Local.
        return Path.home() / 'AppData' / 'Local' / 'Microsoft' / 'Windows' / 'Fonts'

    def _ensure_user_fonts_dir(self):
        """Stellt sicher, dass das benutzerspezifische Fonts-Verzeichnis existiert."""
        fonts_user_dir = self.get_user_fonts_dir()
        try:
            fonts_user_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self.logger.error(f"Fonts-Verzeichnis konnte nicht angelegt werden: {fonts_user_dir} ({exc})")
            raise

        if not fonts_user_dir.exists() or not fonts_user_dir.is_dir():
            raise RuntimeError(f"Fonts-Verzeichnis ist nicht verfügbar: {fonts_user_dir}")

        return fonts_user_dir

    def _log_font_installation_context(self, source_dir: Path, target_dir: Path) -> None:
        """Schreibt eine kurze Diagnose zum verwendeten Font-Pfad ins Log."""
        try:
            local_app_data = os.environ.get('LOCALAPPDATA') or '<nicht gesetzt>'
            self.logger.info(
                "Font-Diagnose | Quelle=%s | Ziel=%s | LOCALAPPDATA=%s | Ziel existiert=%s",
                source_dir,
                target_dir,
                local_app_data,
                target_dir.exists(),
            )
        except Exception:
            pass

    def discover_font_families(self, fonts_directory):
        """Ermittelt verfügbare Font-Familien aus dem Fonts-Verzeichnis."""
        fonts_dir = Path(fonts_directory)
        families = {}

        if not fonts_dir.exists():
            self.logger.warning(f"Fonts-Verzeichnis nicht gefunden: {fonts_dir}")
            return families

        font_files = []
        for ext in self.FONT_EXTENSIONS:
            font_files.extend(fonts_dir.rglob(f'*{ext}'))

        for font_file in sorted(font_files):
            family_name = self._get_font_family_from_file(font_file)
            if not family_name:
                continue
            families.setdefault(family_name, []).append(font_file)

        return dict(sorted(families.items(), key=lambda item: item[0].lower()))

    def get_available_font_families(self, fonts_directory):
        """Liefert die erkannten Font-Familien sortiert zurück."""
        return list(self.discover_font_families(fonts_directory).keys())

    def install_font_family(self, fonts_directory, family_name):
        """Installiert alle Font-Dateien einer ausgewählten Familie."""
        try:
            normalized_family = (family_name or '').strip()
            if not normalized_family:
                return {"success": False, "error": "Keine Font-Familie ausgewählt."}

            family_files = self.discover_font_families(fonts_directory).get(normalized_family, [])
            if not family_files:
                return {
                    "success": False,
                    "error": f"Keine Dateien für Font-Familie gefunden: {normalized_family}"
                }

            installed_fonts = []
            failed_fonts = []
            installed_paths = []
            fonts_user_dir = self._ensure_user_fonts_dir()

            for font_file in family_files:
                if self._install_single_font(font_file):
                    installed_fonts.append(font_file.name)
                    installed_paths.append(str(fonts_user_dir / font_file.name))
                else:
                    failed_fonts.append(font_file.name)

            self._refresh_font_cache()

            return {
                "success": len(installed_fonts) > 0 and not failed_fonts,
                "family_name": normalized_family,
                "installed_fonts": installed_fonts,
                "failed_fonts": failed_fonts,
                "installed_paths": installed_paths,
                "total_processed": len(family_files)
            }
        except Exception as e:
            self.logger.error(f"Fehler bei Installation der Font-Familie {family_name}: {e}")
            return {"success": False, "error": str(e)}
        
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
            refreshed_fonts = []
            failed_fonts = []
            skipped_fonts = []

            # Rekursiv alle Font-Dateien finden
            font_files = []
            
            for ext in self.FONT_EXTENSIONS:
                font_files.extend(fonts_dir.rglob(f'*{ext}'))
            
            self.logger.info(f"Gefundene Font-Dateien: {len(font_files)}")

            fonts_user_dir = self._ensure_user_fonts_dir()
            self._log_font_installation_context(fonts_dir, fonts_user_dir)
            
            for font_file in font_files:
                try:
                    target_file = fonts_user_dir / font_file.name
                    already_installed = target_file.exists()
                    success = self._install_single_font(font_file)
                    if success:
                        if already_installed:
                            if font_file.name not in refreshed_fonts:
                                refreshed_fonts.append(font_file.name)
                        else:
                            installed_fonts.append(font_file.name)
                        self.logger.info(f"Font verarbeitet: {font_file.name}")
                    else:
                        failed_fonts.append(font_file.name)
                        self.logger.warning(f"Font-Installation fehlgeschlagen: {font_file.name}")
                        
                except Exception as e:
                    failed_fonts.append(font_file.name)
                    self.logger.error(f"Fehler bei Font-Installation {font_file.name}: {e}")
            
            # System nur bei echten Neuinstallationen benachrichtigen
            if installed_fonts:
                self._refresh_font_cache()
            
            return {
                "success": len(failed_fonts) == 0,
                "installed_fonts": installed_fonts,
                "refreshed_fonts": refreshed_fonts,
                "failed_fonts": failed_fonts,
                "skipped_fonts": skipped_fonts,
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
            fonts_user_dir = self._ensure_user_fonts_dir()

            # Font-Name aus Datei extrahieren
            font_name = self._get_font_name_from_file(font_file)
            if not font_name:
                font_name = font_file.stem

            # Font-Datei ins User-Verzeichnis kopieren
            target_file = fonts_user_dir / font_file.name

            if target_file.exists():
                self.logger.debug(f"Font-Datei bereits vorhanden, Registrierung wird erneuert: {font_file.name}")
            else:
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

    def _get_font_family_from_file(self, font_file):
        """Leitet aus dem Dateinamen einen Family-Namen ab."""
        try:
            name = font_file.stem
            name = name.replace('_', ' ').replace('-', ' ')
            name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)
            name = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', name)
            tokens = [token for token in name.split() if token]

            while tokens and tokens[-1].isdigit():
                tokens.pop()

            while tokens and tokens[-1].lower() in self.STYLE_TOKENS:
                tokens.pop()

            family_name = ' '.join(tokens).strip()
            if family_name:
                return family_name

            fallback = font_file.parent.name.strip()
            return fallback or font_file.stem
        except Exception as e:
            self.logger.error(f"Fehler bei Family-Erkennung für {font_file}: {e}")
            return font_file.stem
    
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
                self.logger.info(
                    "Font in User-Registry registriert: %s | Pfad=%s | Key=HKCU\\%s",
                    font_name,
                    font_filename,
                    key_path,
                )
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
