#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-Build-Skript für PC-Konfigurator (Unicode-sicher)
Kopiert Fonts, Datei-Vorlagen und Dokumentation auf die gleiche Ebene wie die EXE-Datei
"""

import shutil
import os
import sys
import subprocess
from pathlib import Path


def set_hidden_attribute(path):
    """Setzt das Hidden-Attribut für eine Datei/Ordner unter Windows"""
    try:
        if os.name == 'nt':
            subprocess.run(['attrib', '+h', str(path)], check=True, capture_output=True)
            return True
    except Exception as e:
        print(f"WARNING beim Setzen des hidden-Attributs für {path}: {e}")
    return False


def count_files_recursive(path: Path) -> int:
    """Zählt Dateien rekursiv in einem Verzeichnis."""
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())


def copy_external_directories():
    """Kopiert externe Verzeichnisse in den Build-Ordner"""
    try:
        # Finde das Build-Verzeichnis
        script_dir = Path(__file__).parent.parent.absolute()
        dist_dir = script_dir / "dist"
        
        # Finde den neuesten Build-Ordner (enthält Version im Namen)
        build_folders = [f for f in dist_dir.iterdir() if f.is_dir() and "PC-Konfigurator-Portable-v" in f.name]
        if not build_folders:
            print("ERROR: Kein Build-Ordner gefunden!")
            return False
            
        # Neuester Build nach Änderungszeit
        target_dir = sorted(build_folders, key=lambda p: p.stat().st_mtime)[-1]
        print(f"Target-Verzeichnis: {target_dir}")
        
        # Quellverzeichnisse
        fonts_src = script_dir / "Fonts"
        templates_src = script_dir / "Datei-Vorlagen"
        readme_src = script_dir / "README.md"
        anleitung_src = script_dir / "ANLEITUNG.md"
        buildinfo_src = script_dir / "BUILD-INFO.txt"
        
        # Zielverzeichnisse
        fonts_dest = target_dir / "Fonts"
        templates_dest = target_dir / "Datei-Vorlagen"
        
        # Fonts kopieren (immer frisch, damit nichts aus früheren Builds fehlt)
        if fonts_src.exists():
            if fonts_dest.exists():
                shutil.rmtree(fonts_dest)
            shutil.copytree(fonts_src, fonts_dest)
            print(f"OK Fonts kopiert nach {fonts_dest}")
        else:
            print(f"WARNING Fonts-Verzeichnis {fonts_src} nicht gefunden!")
        
        # Datei-Vorlagen kopieren (immer frisch, damit nichts aus früheren Builds fehlt)
        if templates_src.exists():
            if templates_dest.exists():
                shutil.rmtree(templates_dest)
            shutil.copytree(templates_src, templates_dest)
            print(f"OK Datei-Vorlagen kopiert nach {templates_dest}")
        else:
            print(f"WARNING Datei-Vorlagen-Verzeichnis {templates_src} nicht gefunden!")
        
        # Dokumentation kopieren
        if readme_src.exists():
            shutil.copy2(readme_src, target_dir / "README.md")
            print(f"OK README.md kopiert")
        
        if anleitung_src.exists():
            shutil.copy2(anleitung_src, target_dir / "ANLEITUNG.md")
            print(f"OK ANLEITUNG.md kopiert")
        
        if buildinfo_src.exists():
            shutil.copy2(buildinfo_src, target_dir / "BUILD-INFO.txt")
            print(f"OK BUILD-INFO.txt kopiert")
        
        # Statistiken + Verifikation
        font_files = list(fonts_dest.rglob("*.*")) if fonts_dest.exists() else []
        template_files = list(templates_dest.rglob("*.*")) if templates_dest.exists() else []
        src_font_count = count_files_recursive(fonts_src)
        src_template_count = count_files_recursive(templates_src)
        dst_font_count = count_files_recursive(fonts_dest)
        dst_template_count = count_files_recursive(templates_dest)

        if fonts_src.exists() and dst_font_count != src_font_count:
            raise RuntimeError(f"Fonts unvollständig kopiert: src={src_font_count}, dst={dst_font_count}")
        if templates_src.exists() and dst_template_count != src_template_count:
            raise RuntimeError(f"Datei-Vorlagen unvollständig kopiert: src={src_template_count}, dst={dst_template_count}")

        folder_name = target_dir.name
        
        print(f"OK {len(font_files)} Font-Dateien kopiert")
        print(f"OK {len(template_files)} Template-Dateien kopiert")
        print(f"OK Ordnername: {folder_name}")
        
        # Hidden-Attribute setzen
        internal_dir = target_dir / "_internal"
        if internal_dir.exists():
            if set_hidden_attribute(internal_dir):
                print(f"OK Hidden-Attribut gesetzt für _internal")
            else:
                print(f"WARNING Hidden-Attribut für _internal konnte nicht gesetzt werden")
        
        logs_dir = target_dir / "logs"
        if logs_dir.exists():
            if set_hidden_attribute(logs_dir):
                print(f"OK Hidden-Attribut gesetzt für logs")
            else:
                print(f"WARNING Hidden-Attribut für logs konnte nicht gesetzt werden")
        else:
            # logs-Ordner erstellen und hidden setzen
            logs_dir.mkdir(exist_ok=True)
            if set_hidden_attribute(logs_dir):
                print(f"OK logs-Ordner erstellt und Hidden-Attribut gesetzt")
        
        return True
        
    except Exception as e:
        print(f"FEHLER beim Kopieren: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("POST-BUILD-SCRIPT WIRD AUSGEFÜHRT...")
    print("=" * 50)
    
    success = copy_external_directories()
    if success:
        print("SUCCESS Post-Build erfolgreich abgeschlossen!")
    else:
        print("ERROR Post-Build mit Fehlern beendet!")
        sys.exit(1)