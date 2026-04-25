"""
Datei-Synchronisation Module
============================

Synchronisiert Datei-Vorlagen zwischen Quell- und Zielverzeichnis.
Portiert aus dem ursprünglichen PowerShell-Skript (robocopy-Funktionalität).
"""

import os
import shutil
import logging
from pathlib import Path
import subprocess
import threading
from datetime import datetime


class FileSync:
    """Klasse zur Synchronisation von Dateien und Verzeichnissen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cancel_sync = False
        
        # Ausgeschlossene Dateien und Verzeichnisse (wie im PowerShell-Skript)
        self.exclude_files = [
            "Thumbs.db",
            "Muell.txt",
            ".DS_Store",
            "desktop.ini"
        ]
        
        self.exclude_directories = [
            ".git",
            ".svn",
            "__pycache__",
            "node_modules",
            ".tmp",
            "Temp"
        ]
    
    def sync_directories(self, source_path, target_path, use_robocopy=True):
        """Verzeichnisse synchronisieren"""
        try:
            self.cancel_sync = False
            source_path = Path(source_path)
            target_path = Path(target_path)
            
            self.logger.info(f"Synchronisation gestartet: {source_path} -> {target_path}")
            
            # Quellverzeichnis prüfen
            if not source_path.exists():
                return {"success": False, "error": f"Quellverzeichnis nicht gefunden: {source_path}"}
            
            # Zielverzeichnis erstellen falls nicht vorhanden
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Robocopy verwenden wenn verfügbar und gewünscht
            if use_robocopy and self._is_robocopy_available():
                return self._sync_with_robocopy(source_path, target_path)
            else:
                return self._sync_with_python(source_path, target_path)
                
        except Exception as e:
            self.logger.error(f"Fehler bei Verzeichnis-Synchronisation: {e}")
            return {"success": False, "error": str(e)}
    
    def cancel_synchronization(self):
        """Synchronisation abbrechen"""
        self.cancel_sync = True
        self.logger.info("Synchronisation-Abbruch angefordert")
    
    def _is_robocopy_available(self):
        """Prüfen, ob robocopy verfügbar ist"""
        try:
            subprocess.run(["robocopy", "/?"], capture_output=True, check=False)
            return True
        except FileNotFoundError:
            return False
    
    def _sync_with_robocopy(self, source_path, target_path):
        """Synchronisation mit robocopy (wie im PowerShell-Skript)"""
        try:
            self.logger.info("Verwende robocopy für Synchronisation")
            
            # Robocopy-Log-Verzeichnis
            log_dir = Path(__file__).parent.parent / "logs" / "robocopy"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Log-Datei mit Zeitstempel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"robocopy_log_{timestamp}.log"
            
            # Ausgeschlossene Dateien für robocopy
            exclude_files_param = " ".join([f"\"{f}\"" for f in self.exclude_files])
            exclude_dirs_param = " ".join([f"\"{d}\"" for d in self.exclude_directories])
            
            # Robocopy-Kommando erstellen
            # /E = Alle Unterverzeichnisse einschließlich leere
            # /XO = Ältere Dateien ausschließen  
            # /MT:5 = Multi-Threading mit 5 Threads
            # /LOG = Log-Datei
            # /TEE = Output in Konsole und Log
            # /XF = Ausgeschlossene Dateien
            # /XD = Ausgeschlossene Verzeichnisse
            cmd = [
                "robocopy",
                str(source_path),
                str(target_path),
                "/E",           # Alle Unterverzeichnisse
                "/XO",          # Ältere Dateien überspringen
                "/MT:5",        # 5 Threads
                "/LOG:" + str(log_file),  # Log-Datei
                "/TEE",         # Output in Konsole und Log
                "/NP",          # Kein Progress-Prozentsatz
                "/NC",          # Keine Datei-Klassen
                "/NS",          # Keine Datei-Größen
                "/NFL"          # Keine Datei-Namen-Liste
            ]
            
            # Ausgeschlossene Dateien hinzufügen
            if self.exclude_files:
                cmd.extend(["/XF"] + self.exclude_files)
                
            # Ausgeschlossene Verzeichnisse hinzufügen
            if self.exclude_directories:
                cmd.extend(["/XD"] + self.exclude_directories)
            
            # Robocopy ausführen
            self.logger.info(f"Führe robocopy aus: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            # Robocopy Exit-Codes auswerten
            # 0 = Keine Dateien kopiert
            # 1 = Dateien erfolgreich kopiert
            # 2 = Zusätzliche Dateien/Verzeichnisse gefunden
            # 3 = 1 + 2
            # >=8 = Fehler
            if result.returncode < 8:
                self.logger.info(f"Robocopy abgeschlossen mit Exit-Code: {result.returncode}")
                self._clean_old_robocopy_logs(log_dir)
                
                return {
                    "success": True,
                    "message": "Datei-Synchronisation mit robocopy erfolgreich",
                    "log_file": str(log_file),
                    "exit_code": result.returncode,
                    "output": result.stdout
                }
            else:
                self.logger.error(f"Robocopy fehlgeschlagen mit Exit-Code: {result.returncode}")
                return {
                    "success": False,
                    "error": f"Robocopy Fehler (Exit-Code {result.returncode}): {result.stderr}",
                    "output": result.stdout
                }
                
        except Exception as e:
            self.logger.error(f"Fehler bei robocopy-Synchronisation: {e}")
            return {"success": False, "error": str(e)}
    
    def _sync_with_python(self, source_path, target_path):
        """Synchronisation mit Python (Fallback)"""
        try:
            self.logger.info("Verwende Python für Synchronisation")
            
            copied_files = 0
            skipped_files = 0
            errors = []
            
            # Alle Dateien im Quellverzeichnis durchlaufen
            for source_file in source_path.rglob("*"):
                if self.cancel_sync:
                    return {"success": False, "error": "Synchronisation abgebrochen"}
                
                # Überspringe Verzeichnisse
                if source_file.is_dir():
                    continue
                
                # Relativen Pfad berechnen
                rel_path = source_file.relative_to(source_path)
                target_file = target_path / rel_path
                
                # Ausgeschlossene Dateien/Verzeichnisse prüfen
                if self._should_exclude_file(source_file, rel_path):
                    continue
                
                try:
                    # Zielverzeichnis erstellen
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Datei kopieren nur wenn sie neuer ist oder nicht existiert
                    if not target_file.exists() or source_file.stat().st_mtime > target_file.stat().st_mtime:
                        shutil.copy2(source_file, target_file)
                        copied_files += 1
                        self.logger.debug(f"Kopiert: {rel_path}")
                    else:
                        skipped_files += 1
                        self.logger.debug(f"Übersprungen (nicht neuer): {rel_path}")
                        
                except Exception as e:
                    error_msg = f"Fehler beim Kopieren von {rel_path}: {e}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
            
            self.logger.info(f"Python-Synchronisation abgeschlossen: {copied_files} kopiert, {skipped_files} übersprungen")
            
            return {
                "success": True,
                "message": f"Datei-Synchronisation erfolgreich: {copied_files} Dateien kopiert, {skipped_files} übersprungen",
                "copied_files": copied_files,
                "skipped_files": skipped_files,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Python-Synchronisation: {e}")
            return {"success": False, "error": str(e)}
    
    def _should_exclude_file(self, file_path, rel_path):
        """Prüfen, ob Datei ausgeschlossen werden soll"""
        # Dateiname prüfen
        if file_path.name in self.exclude_files:
            return True
            
        # Verzeichnisname in Pfad prüfen
        for part in rel_path.parts:
            if part in self.exclude_directories:
                return True
                
        # Versteckte Dateien (beginnen mit .)
        if file_path.name.startswith('.'):
            return True
            
        return False
    
    def _clean_old_robocopy_logs(self, log_dir, keep_count=3):
        """Alte robocopy-Logs bereinigen (nur die neuesten behalten)"""
        try:
            log_files = list(log_dir.glob("robocopy_log_*.log"))
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Alte Logs löschen (nur die neuesten behalten)
            for log_file in log_files[keep_count:]:
                try:
                    log_file.unlink()
                    self.logger.debug(f"Alte robocopy-Log gelöscht: {log_file}")
                except Exception as e:
                    self.logger.warning(f"Fehler beim Löschen von {log_file}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Fehler bei Robocopy-Log-Bereinigung: {e}")
    
    def get_sync_statistics(self, source_path, target_path):
        """Synchronisations-Statistiken ermitteln"""
        try:
            source_path = Path(source_path)
            target_path = Path(target_path)
            
            if not source_path.exists():
                return {"error": "Quellverzeichnis existiert nicht"}
                
            source_files = []
            for file_path in source_path.rglob("*"):
                if file_path.is_file() and not self._should_exclude_file(file_path, file_path.relative_to(source_path)):
                    source_files.append(file_path)
            
            target_files = []
            if target_path.exists():
                for file_path in target_path.rglob("*"):
                    if file_path.is_file():
                        target_files.append(file_path)
            
            return {
                "source_file_count": len(source_files),
                "target_file_count": len(target_files),
                "source_size": sum(f.stat().st_size for f in source_files),
                "target_size": sum(f.stat().st_size for f in target_files) if target_files else 0,
                "source_path_exists": source_path.exists(),
                "target_path_exists": target_path.exists()
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Statistik-Ermittlung: {e}")
            return {"error": str(e)}