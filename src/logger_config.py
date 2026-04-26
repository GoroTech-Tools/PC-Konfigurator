"""
Logging-Konfiguration
=====================

Konfiguriert das Logging-System für die PC-Konfigurator-Anwendung.
Basiert auf dem Logging-System des ursprünglichen PowerShell-Skripts.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import sys


def setup_logging(log_level=logging.INFO):
    """Logging-System konfigurieren"""
    
    # Log-Verzeichnis erstellen
    if getattr(sys, 'frozen', False):
        log_dir = Path(sys.executable).resolve().parent / "logs"
    else:
        log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log-Datei mit Zeitstempel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"PC-Konfigurator_{timestamp}.log"
    
    # Root-Logger konfigurieren
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Bestehende Handler entfernen
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter definieren
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(name)s - %(message)s'
    )
    
    # File Handler - rotiert automatisch
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console Handler - nur für Errors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Alte Log-Dateien bereinigen
    clean_old_logs(log_dir)
    
    # Initial-Log
    logger.info("=" * 60)
    logger.info("PC-Konfigurator Python - Logging gestartet")
    logger.info(f"Log-Datei: {log_file}")
    logger.info("=" * 60)
    
    return logger


def clean_old_logs(log_dir, max_logs=3):
    """Alte Log-Dateien bereinigen (nur die neuesten behalten)"""
    try:
        log_files = list(log_dir.glob("PC-Konfigurator_*.log"))
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Alte Logs löschen
        for log_file in log_files[max_logs:]:
            try:
                log_file.unlink()
                print(f"Alte Log-Datei gelöscht: {log_file.name}")
            except Exception as e:
                print(f"Fehler beim Löschen von {log_file}: {e}")
                
    except Exception as e:
        print(f"Fehler bei Log-Bereinigung: {e}")


class CustomHandler(logging.Handler):
    """Custom Handler für GUI-Ausgabe"""
    
    def __init__(self, gui_callback=None):
        super().__init__()
        self.gui_callback = gui_callback
    
    def emit(self, record):
        if self.gui_callback:
            try:
                msg = self.format(record)
                self.gui_callback(msg)
            except Exception:
                # Ignore errors in GUI callback
                pass


def add_gui_handler(gui_callback, log_level=logging.INFO):
    """GUI-Handler zum Root-Logger hinzufügen"""
    try:
        logger = logging.getLogger()
        
        # GUI-Handler erstellen
        gui_handler = CustomHandler(gui_callback)
        gui_handler.setLevel(log_level)
        
        # Formatter für GUI
        gui_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        gui_handler.setFormatter(gui_formatter)
        
        # Handler hinzufügen
        logger.addHandler(gui_handler)
        
        return gui_handler
        
    except Exception as e:
        print(f"Fehler beim Hinzufügen des GUI-Handlers: {e}")
        return None


def remove_gui_handler(gui_handler):
    """GUI-Handler vom Root-Logger entfernen"""
    try:
        if gui_handler:
            logger = logging.getLogger()
            logger.removeHandler(gui_handler)
    except Exception as e:
        print(f"Fehler beim Entfernen des GUI-Handlers: {e}")


def get_log_files():
    """Alle Log-Dateien im Log-Verzeichnis auflisten"""
    try:
        if getattr(sys, 'frozen', False):
            log_dir = Path(sys.executable).resolve().parent / "logs"
        else:
            log_dir = Path(__file__).resolve().parent.parent / "logs"
        if not log_dir.exists():
            return []
            
        log_files = list(log_dir.glob("*.log"))
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        return log_files
        
    except Exception as e:
        print(f"Fehler beim Auflisten der Log-Dateien: {e}")
        return []


def read_latest_log():
    """Inhalt der neuesten Log-Datei lesen"""
    try:
        log_files = get_log_files()
        if not log_files:
            return "Keine Log-Dateien gefunden."
            
        latest_log = log_files[0]
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            return f.read()
            
    except Exception as e:
        return f"Fehler beim Lesen der Log-Datei: {e}"


def clear_all_logs():
    """Alle Log-Dateien löschen"""
    try:
        log_files = get_log_files()
        deleted_count = 0
        
        for log_file in log_files:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Fehler beim Löschen von {log_file}: {e}")
                
        return f"{deleted_count} Log-Datei(en) gelöscht."
        
    except Exception as e:
        return f"Fehler beim Löschen der Log-Dateien: {e}"


# Logging-Level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}