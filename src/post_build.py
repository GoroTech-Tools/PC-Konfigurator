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


def _env_true(name: str) -> bool:
    """Interpretiert gängige True-Werte aus Umgebungsvariablen."""
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


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
    """Zählt Dateien rekursiv in einem Verzeichnis (Long-Path-sicher)."""
    if not path.exists():
        return 0
    # os.walk ist robuster mit langen/Unicode-Pfaden als Path.rglob
    count = 0
    for _, _, files in os.walk(str(path)):
        count += len(files)
    return count


def copytree_resilient(src: Path, dst: Path) -> tuple[int, int, list[tuple[Path, str]]]:
    """Kopiert einen Verzeichnisbaum fehlertolerant und liefert Statistik zurück.

    Rückgabe:
      (copied_count, source_count, failures)
    """
    copied_count = 0
    source_count = 0
    failures: list[tuple[Path, str]] = []

    dst.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        rel_root = root_path.relative_to(src)
        dst_root = dst / rel_root
        dst_root.mkdir(parents=True, exist_ok=True)

        for directory in dirs:
            (dst_root / directory).mkdir(parents=True, exist_ok=True)

        for filename in files:
            source_count += 1
            source_file = root_path / filename
            target_file = dst_root / filename
            try:
                # Prüfe ob Quell-Datei wirklich existiert und lesbar ist
                # (OneDrive-Placeholder sind manchmal nur Ghost-Dateien)
                if not source_file.exists():
                    failures.append((source_file, "OneDrive Placeholder oder nicht vorhanden"))
                    continue
                
                # Versuche Datei zu öffnen um zu prüfen ob sie wirklich lesbar ist
                try:
                    with open(str(source_file), 'rb'):
                        pass
                except (IOError, OSError) as read_error:
                    failures.append((source_file, f"Nicht lesbar (OneDrive): {read_error}"))
                    continue
                
                # \\?\ Präfix aktiviert Long-Path-Support (>260 Zeichen, Unicode)
                src_str = "\\\\?\\" + str(source_file.resolve())
                dst_str = "\\\\?\\" + str(target_file.resolve())
                shutil.copy2(src_str, dst_str)
                copied_count += 1
            except Exception as exc:
                # Wenn Kopieren fehlschlägt, lösche die (ggf. leere) Zieldatei
                try:
                    if target_file.exists():
                        target_file.unlink()
                except Exception:
                    pass
                failures.append((source_file, str(exc)))

    return copied_count, source_count, failures


def rmtree_longpath(path: Path) -> None:
    """Löscht ein Verzeichnis rekursiv, auch bei langen/Unicode-Pfaden (Windows)."""
    if os.name == 'nt':
        # robocopy mit leerem Temp-Ordner ist der zuverlässigste Weg für lange Pfade
        import tempfile
        with tempfile.TemporaryDirectory() as empty_dir:
            subprocess.run(
                ['robocopy', empty_dir, str(path), '/MIR', '/NFL', '/NDL', '/NJH', '/NJS'],
                capture_output=True
            )
        try:
            os.rmdir(str(path))
        except Exception:
            pass
    else:
        shutil.rmtree(path)


def copy_external_directories():
    """Kopiert externe Verzeichnisse in den Build-Ordner"""
    try:
        allow_partial_templates = _env_true("PCONFIG_ALLOW_PARTIAL_TEMPLATES")

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
        font_failures: list[tuple[Path, str]] = []
        tpl_failures: list[tuple[Path, str]] = []
        
        # Fonts kopieren (immer frisch, damit nichts aus früheren Builds fehlt)
        if fonts_src.exists():
            if fonts_dest.exists():
                rmtree_longpath(fonts_dest)
            font_copied, font_source, font_failures = copytree_resilient(fonts_src, fonts_dest)
            print(f"OK Fonts kopiert nach {fonts_dest}")
            if font_failures:
                print(f"WARNING {len(font_failures)} Font-Datei(en) konnten nicht kopiert werden:")
                for missing_file, error_message in font_failures[:10]:
                    print(f"  - {missing_file}: {error_message}")
                if len(font_failures) > 10:
                    print(f"  ... und {len(font_failures) - 10} weitere")
        else:
            print(f"WARNING Fonts-Verzeichnis {fonts_src} nicht gefunden!")
        
        # Datei-Vorlagen kopieren (immer frisch, damit nichts aus früheren Builds fehlt)
        if templates_src.exists():
            if templates_dest.exists():
                rmtree_longpath(templates_dest)
            tpl_copied, tpl_source, tpl_failures = copytree_resilient(templates_src, templates_dest)
            
            # Bereinige fehlgeschlagene Dateien (OneDrive-Placeholder, Ghost-Dateien)
            for failed_file, _ in tpl_failures:
                try:
                    # Berechne Zieldatei-Pfad
                    relative_path = failed_file.relative_to(templates_src)
                    target_file = templates_dest / relative_path
                    if target_file.exists():
                        target_file.unlink()
                        print(f"  - Bereinigt: {target_file.name} (OneDrive-Placeholder)")
                except Exception as e:
                    print(f"  - Fehler beim Bereinigen von {failed_file}: {e}")
            
            # Zusätzliche Bereinigung: Lösche alle leeren Dateien (Ghost-Dateien von OneDrive)
            for root, dirs, files in os.walk(str(templates_dest)):
                for filename in files:
                    filepath = Path(root) / filename
                    try:
                        if filepath.exists() and filepath.stat().st_size == 0:
                            filepath.unlink()
                            print(f"  - Gelöscht: {filepath.name} (leere Ghost-Datei)")
                    except Exception:
                        pass
            
            print(f"OK Datei-Vorlagen kopiert nach {templates_dest}")
            if tpl_failures:
                print(f"WARNING {len(tpl_failures)} Datei(en) konnten nicht kopiert werden (z.B. OneDrive-Placeholder):")
                for missing_file, error_message in tpl_failures[:10]:
                    print(f"  - {missing_file}: {error_message}")
                if len(tpl_failures) > 10:
                    print(f"  ... und {len(tpl_failures) - 10} weitere")
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
            raise RuntimeError(
                f"Fonts unvollständig kopiert: src={src_font_count}, dst={dst_font_count}. "
                "Bitte OneDrive-Dateien lokal verfügbar machen."
            )

        if fonts_src.exists() and font_failures:
            raise RuntimeError(
                f"{len(font_failures)} Font-Datei(en) konnten nicht kopiert werden. "
                "Bitte OneDrive-Dateien lokal verfügbar machen."
            )
        if templates_src.exists() and dst_template_count != src_template_count:
            message = (
                "Datei-Vorlagen unvollständig kopiert "
                f"(src={src_template_count}, dst={dst_template_count})."
            )
            if allow_partial_templates:
                print(f"WARNING {message} Build wird fortgesetzt (PCONFIG_ALLOW_PARTIAL_TEMPLATES=1).")
            else:
                raise RuntimeError(
                    f"{message} Bitte OneDrive-Dateien lokal verfügbar machen. "
                    "Optional für Tests: PCONFIG_ALLOW_PARTIAL_TEMPLATES=1"
                )

        if tpl_failures and not allow_partial_templates:
            raise RuntimeError(
                f"{len(tpl_failures)} Datei(en) aus 'Datei-Vorlagen' konnten nicht kopiert werden. "
                "Bitte OneDrive-Dateien lokal verfügbar machen. "
                "Optional für Tests: PCONFIG_ALLOW_PARTIAL_TEMPLATES=1"
            )

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