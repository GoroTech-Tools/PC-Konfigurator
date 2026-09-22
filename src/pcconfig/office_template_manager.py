"""
Office Template Manager
======================

Verwaltet Office-Vorlagendateien (Normal.dotm, Mappe.xltx, NormalEmail.dotm)
"""

import os
import shutil
import time
from pathlib import Path
import logging
import zipfile
import tempfile
from xml.etree import ElementTree as ET
from pcconfig.safe_template_processor import SafeTemplateProcessor
from fs_retry import retry_on_oserror


class OfficeTemplateManager:
    def _read_word_font_info_from_template(self, template_path: Path):
        """Liest die Standard-Schrift aus word/styles.xml (docDefaults bzw. Normal/Standard-Stil)."""
        try:
            with zipfile.ZipFile(template_path, 'r') as zf:
                names = zf.namelist()
                styles_entry = next((n for n in names if n.lower() == 'word/styles.xml'), None)
                if not styles_entry:
                    return None
                styles_xml = zf.read(styles_entry)

            root = ET.fromstring(styles_xml)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            # Die Konfiguration ändert ausschließlich die Absatzformatvorlagen
            # Standard/Normal und Kein Leerraum/No Spacing. Diese direkten
            # Stildefinitionen müssen daher auch für die Verifikation Vorrang
            # vor globalen docDefaults haben.
            rpr = None
            target_style_ids = {'normal', 'nospacing', 'no spacing'}
            target_style_names = {'standard', 'normal', 'kein leerraum', 'no spacing'}
            for style in root.findall('.//w:style', ns):
                style_id = style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId', '')
                style_type = style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type', '')
                name_element = style.find('w:name', ns)
                style_name = name_element.attrib.get('{' + ns['w'] + '}val', '') if name_element is not None else ''
                if style_type == 'paragraph' and (
                    style_id.strip().casefold() in target_style_ids
                    or style_name.strip().casefold() in target_style_names
                ):
                    candidate = style.find('w:rPr', ns)
                    if candidate is not None:
                        rpr = candidate
                        if style_id.strip().casefold() in {'normal', 'standard'} or style_name.strip().casefold() in {'standard', 'normal'}:
                            break

            # Fallback für Vorlagen ohne explizite Ziel-Formatvorlagen.
            if rpr is None:
                rpr = root.find('.//w:docDefaults/w:rPrDefault/w:rPr', ns)

            if rpr is None:
                return None

            rfonts = rpr.find('w:rFonts', ns)
            if rfonts is None:
                return None

            font_name = (
                rfonts.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                or rfonts.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi')
                or rfonts.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs')
                or ''
            ).strip()

            sz = rpr.find('w:sz', ns)
            raw_size = ''
            if sz is not None:
                raw_size = sz.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '').strip()

            if not raw_size:
                # Stil definiert nur die Schriftart und erbt die Größe laut OOXML
                # regulär aus den docDefaults (z. B. bei NormalEmail.dotm üblich).
                default_sz = root.find('.//w:docDefaults/w:rPrDefault/w:rPr/w:sz', ns)
                if default_sz is not None:
                    raw_size = default_sz.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '').strip()

            if not font_name:
                return None

            size_value = None
            if raw_size:
                try:
                    size_value = int(round(float(raw_size) / 2.0))
                except Exception:
                    size_value = None

            return {
                'font_name': font_name,
                'font_size': size_value,
            }
        except Exception as exc:
            self.logger.debug(f"Word-Font konnte nicht aus {template_path} gelesen werden: {exc}")
            return None

    def _read_excel_font_info_from_template(self, template_path: Path):
        """Liest die Default-Schrift aus xl/styles.xml (font[0]) einer .xltx/.xlsx-Datei."""
        try:
            with zipfile.ZipFile(template_path, 'r') as zf:
                styles_xml = zf.read('xl/styles.xml')

            root = ET.fromstring(styles_xml)
            ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            font = root.find('.//x:fonts/x:font', ns)
            if font is None:
                return None

            name_el = font.find('x:name', ns)
            size_el = font.find('x:sz', ns)

            font_name = name_el.attrib.get('val', '').strip() if name_el is not None else ''
            raw_size = size_el.attrib.get('val', '').strip() if size_el is not None else ''

            if not font_name:
                return None

            try:
                size_value = int(round(float(raw_size))) if raw_size else None
            except Exception:
                size_value = None

            return {
                'font_name': font_name,
                'font_size': size_value,
            }
        except Exception as exc:
            self.logger.debug(f"Excel-Font konnte nicht aus {template_path} gelesen werden: {exc}")
            return None

    @staticmethod
    def _format_font_info(font_info):
        """Formatiert Font-Infos als lesbaren Text für die GUI."""
        if not font_info:
            return "Unbekannt"
        if isinstance(font_info, dict):
            name = str(font_info.get('font_name', '')).strip()
            size = font_info.get('font_size')
            if name and size:
                return f"{name} {size}pt"
            if name:
                return name
            return "Unbekannt"
        return str(font_info)

    @staticmethod
    def _normalize_font_name(name):
        if not name:
            return ""
        return str(name).strip().lower()

    @staticmethod
    def _size_matches(actual, expected):
        try:
            if actual is None:
                return False
            return int(round(float(actual))) == int(round(float(expected)))
        except Exception:
            return False

    def verify_user_template_fonts(self, font_name, font_size_word, font_size_excel, font_size_outlook=12):
        """Verifiziert, ob die Ziel-Templates im Benutzerprofil die erwarteten Font-Defaults tragen."""
        expected_font = str(font_name or '').strip()
        details = {}

        # Word Normal.dotm
        normal_target = self.target_paths.get('normal_dotm')
        if not normal_target or not normal_target.exists():
            details['normal_dotm'] = {
                'ok': False,
                'reason': 'Ziel-Template nicht vorhanden',
                'actual': None,
            }
        else:
            info = self._read_word_font_info_from_template(normal_target)
            if not info:
                details['normal_dotm'] = {
                    'ok': False,
                    'reason': 'Schrift nicht aus Template lesbar',
                    'actual': None,
                }
            else:
                name_ok = self._normalize_font_name(info.get('font_name')) == self._normalize_font_name(expected_font)
                size_ok = self._size_matches(info.get('font_size'), font_size_word)
                details['normal_dotm'] = {
                    'ok': bool(name_ok and size_ok),
                    'reason': None if (name_ok and size_ok) else 'Abweichende Word-Defaults',
                    'actual': info,
                }

        # Excel Mappe.xltx
        excel_target = self.target_paths.get('mappe_xltx')
        if not excel_target or not excel_target.exists():
            details['mappe_xltx'] = {
                'ok': False,
                'reason': 'Ziel-Template nicht vorhanden',
                'actual': None,
            }
        else:
            info = self._read_excel_font_info_from_template(excel_target)
            if not info:
                details['mappe_xltx'] = {
                    'ok': False,
                    'reason': 'Schrift nicht aus Template lesbar',
                    'actual': None,
                }
            else:
                name_ok = self._normalize_font_name(info.get('font_name')) == self._normalize_font_name(expected_font)
                size_ok = self._size_matches(info.get('font_size'), font_size_excel)
                details['mappe_xltx'] = {
                    'ok': bool(name_ok and size_ok),
                    'reason': None if (name_ok and size_ok) else 'Abweichende Excel-Defaults',
                    'actual': info,
                }

        # Excel book.xltx (zusätzliche Vorlage)
        book_target = self.target_paths.get('book_xltx')
        if not book_target or not book_target.exists():
            details['book_xltx'] = {
                'ok': False,
                'reason': 'Ziel-Template nicht vorhanden',
                'actual': None,
            }
        else:
            info = self._read_excel_font_info_from_template(book_target)
            if not info:
                details['book_xltx'] = {
                    'ok': False,
                    'reason': 'Schrift nicht aus Template lesbar',
                    'actual': None,
                }
            else:
                name_ok = self._normalize_font_name(info.get('font_name')) == self._normalize_font_name(expected_font)
                size_ok = self._size_matches(info.get('font_size'), font_size_excel)
                details['book_xltx'] = {
                    'ok': bool(name_ok and size_ok),
                    'reason': None if (name_ok and size_ok) else 'Abweichende Excel-Defaults',
                    'actual': info,
                }

        # Outlook NormalEmail.dotm
        outlook_target = self.target_paths.get('normal_email_dotm')
        if not outlook_target or not outlook_target.exists():
            details['normal_email_dotm'] = {
                'ok': False,
                'reason': 'Ziel-Template nicht vorhanden',
                'actual': None,
            }
        else:
            info = self._read_word_font_info_from_template(outlook_target)
            if not info:
                details['normal_email_dotm'] = {
                    'ok': False,
                    'reason': 'Schrift nicht aus Template lesbar',
                    'actual': None,
                }
            else:
                name_ok = self._normalize_font_name(info.get('font_name')) == self._normalize_font_name(expected_font)
                size_ok = self._size_matches(info.get('font_size'), font_size_outlook)
                details['normal_email_dotm'] = {
                    'ok': bool(name_ok and size_ok),
                    'reason': None if (name_ok and size_ok) else 'Abweichende Outlook-Template-Defaults',
                    'actual': info,
                }

        success = all(item.get('ok') for item in details.values()) if details else False
        return {
            'success': success,
            'details': details,
            'expected': {
                'font_name': expected_font,
                'font_size_word': int(font_size_word),
                'font_size_outlook': int(font_size_outlook),
                'font_size_excel': int(font_size_excel),
            },
        }

    def check_templates_exist(self):
        """Prüft, ob alle Templates existieren. Gibt Dict zurück."""
        result = {}
        for key, path in self.source_templates.items():
            result[key] = path.exists()
        return result

    def get_current_fonts_in_templates(self):
        """Liefert die aktuelle Schriftart/-größe der Templates (soweit möglich). Gibt Dict zurück."""
        fonts = {}
        # Word/Outlook: Versuche Font auszulesen
        for key in ['normal_dotm', 'normal_email_dotm']:
            path = self.source_templates.get(key)
            if path and path.exists():
                try:
                    font_info = self._read_word_font_info_from_template(path)
                    if not font_info:
                        font_info = self.safe_processor.get_word_template_font_info(path)
                    fonts[key] = self._format_font_info(font_info)
                except Exception as e:
                    fonts[key] = f"Fehler: {e}"
            else:
                fonts[key] = "Nicht vorhanden"
        # Excel: Default-Font aus styles.xml lesen
        key = 'mappe_xltx'
        path = self.source_templates.get(key)
        if path and path.exists():
            excel_info = self._read_excel_font_info_from_template(path)
            fonts[key] = self._format_font_info(excel_info)
        else:
            fonts[key] = "Nicht vorhanden"

        # Excel Zusatzvorlage book.xltx im Zielprofil
        book_target = self.target_paths.get('book_xltx')
        if book_target and book_target.exists():
            excel_book_info = self._read_excel_font_info_from_template(book_target)
            fonts['book_xltx'] = self._format_font_info(excel_book_info)
        else:
            fonts['book_xltx'] = "Nicht vorhanden"
        return fonts
    
    def __init__(self, app_dir):
        """
        Initialisiert den Office Template Manager
        
        Args:
            app_dir: Verzeichnis der Anwendung
        """
        self.app_dir = Path(app_dir)
        self.logger = logging.getLogger(__name__)
        self.safe_processor = SafeTemplateProcessor()  # Sichere Template-Verarbeitung
        # Template-Pfade definieren
        try:
            self.source_templates = {
                'normal_dotm': self.app_dir / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Normal.dotm",
                'mappe_xltx': self.app_dir / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Mappe.xltx",
                'normal_email_dotm': self.app_dir / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm"
            }
            self._generic_source_templates = dict(self.source_templates)
            self._working_template_dir = None
        except Exception as e:
            self.logger.error(f"Fehler bei source_templates-Initialisierung: {e}")
            self.source_templates = {}
        try:
            self.target_paths = {
                'normal_dotm': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Templates" / "Normal.dotm",
                'mappe_xltx': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART" / "Mappe.xltx",
                'book_xltx': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART" / "book.xltx",
                'normal_email_dotm': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Templates" / "NormalEmail.dotm"
            }
        except Exception as e:
            self.logger.error(f"Fehler bei target_paths-Initialisierung: {e}")
            self.target_paths = {}

    def _get_building_blocks_candidates(self):
        """Liefert potenzielle Word-Building-Blocks-Dateien aus Standardpfaden.

        Der relevante Standardpfad ist pro Nutzer:
        %APPDATA%\\Microsoft\\Document Building Blocks\\<lcid>\\<version>\\Building Blocks.dotx
        Für „Alle Benutzer“ gibt es zusätzlich Installationspfade unter Office,
        aber der user-scoped Pfad ist der klassische Standard für Word.
        """
        standard_dir = self.app_dir / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards"
        roaming_templates = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Templates"
        appdata_building_blocks = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Document Building Blocks"
        possible_lang_versions = [
            "1031",  # Deutsch
            "1033",  # English
            "1030",  # Danish
            "1040",  # Italian
            "1041",  # Japanese
            "2055",  # German (Germany) / fallback
        ]
        version_dirs = ["16", "15", "14"]

        program_roots = []
        for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
            value = os.environ.get(env_name)
            if value:
                program_roots.append(Path(value))
        if not program_roots:
            program_roots.append(Path(r"C:\Program Files"))
            program_roots.append(Path(r"C:\Program Files (x86)"))

        candidate_names = (
            "Building Blocks.dotx",
            "Building Blocks.dotm",
            "BuildingBlocks.dotx",
            "BuildingBlocks.dotm",
            "Document Building Blocks.dotx",
            "Document Building Blocks.dotm",
        )

        candidates = []
        for base in (standard_dir, roaming_templates):
            for name in candidate_names:
                candidates.append(base / name)

        # Exakter, realer Standardpfad für Word-Building-Blocks im User-Profil.
        exact_user_building_blocks = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Document Building Blocks' / '1031' / '16' / 'Building Blocks.dotx'
        candidates.append(exact_user_building_blocks)

        for lang in possible_lang_versions:
            for version in version_dirs:
                candidates.append(appdata_building_blocks / lang / version / "Building Blocks.dotx")
                candidates.append(appdata_building_blocks / lang / version / "Building Blocks.dotm")

        for root in program_roots:
            for lang in possible_lang_versions:
                for version in version_dirs:
                    for suffix in (root / "Microsoft Office" / "root" / "Office" / version, root / "Microsoft Office" / "root" / "Document Building Blocks"):
                        candidates.append(suffix / lang / version / "Building Blocks.dotx")
                        candidates.append(suffix / lang / version / "Building Blocks.dotm")
                    candidates.append(root / "Microsoft Office" / "root" / "Document Building Blocks" / lang / version / "Building Blocks.dotx")
                    candidates.append(root / "Microsoft Office" / "root" / "Document Building Blocks" / lang / version / "Building Blocks.dotm")
                    candidates.append(root / "Microsoft Office" / "root" / "Office" / version / "Document Building Blocks" / lang / version / "Building Blocks.dotx")
                    candidates.append(root / "Microsoft Office" / "root" / "Office" / version / "Document Building Blocks" / lang / version / "Building Blocks.dotm")

        # Deduplizieren, ohne die ursprüngliche Reihenfolge zu verlieren.
        unique = []
        seen = set()
        for candidate in candidates:
            resolved = str(candidate)
            if resolved not in seen:
                seen.add(resolved)
                unique.append(candidate)
        return unique

    def get_user_building_blocks_path(self):
        """Ermittelt die persönliche Building-Blocks-Datei des aktuellen Benutzers."""
        building_blocks_dir = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Document Building Blocks'
        preferred = building_blocks_dir / '1031' / '16' / 'Building Blocks.dotx'
        candidates = [preferred]
        if building_blocks_dir.is_dir():
            candidates.extend(sorted(building_blocks_dir.glob('*/*/Building Blocks.dotx')))
        seen = set()
        for candidate in candidates:
            resolved = str(candidate)
            if resolved in seen:
                continue
            seen.add(resolved)
            if candidate.is_file():
                return candidate
        return preferred

    def sync_user_building_blocks_backup(self, target_datei_vorlagen_dir):
        """Spiegelt Building Blocks zwischen Benutzerprofil und Vorlagenablage.

        Die jeweils neuere Datei gewinnt. Eine fehlende Benutzerdatei wird aus
        der Ablage wiederhergestellt; eine fehlende Ablage wird aus dem Profil
        angelegt. Andere Dateien im Zielordner werden nicht verändert.
        """
        user_path = self.get_user_building_blocks_path()
        backup_path = Path(target_datei_vorlagen_dir) / 'Sonstiges' / 'Building Blocks' / 'Building Blocks.dotx'
        try:
            user_exists = user_path.is_file()
            backup_exists = backup_path.is_file()
            if not user_exists and not backup_exists:
                return {
                    'success': True,
                    'status': 'skipped',
                    'message': 'Keine persönliche Building-Blocks-Datei vorhanden.',
                }

            def copy_with_retry(source_path: Path, destination_path: Path) -> None:
                def copy_action() -> None:
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, destination_path)

                retry_on_oserror(copy_action)

            if backup_exists and (not user_exists or backup_path.stat().st_mtime > user_path.stat().st_mtime):
                copy_with_retry(backup_path, user_path)
                action = 'restored'
                message = f'Building Blocks aus der Sicherung wiederhergestellt: {user_path}'
            elif user_exists and (not backup_exists or user_path.stat().st_mtime > backup_path.stat().st_mtime):
                copy_with_retry(user_path, backup_path)
                action = 'backed_up'
                message = f'Building Blocks in die Vorlagenablage gesichert: {backup_path}'
            else:
                action = 'unchanged'
                message = 'Building-Blocks-Sicherung und Benutzerdatei sind bereits aktuell.'

            self.logger.info(message)
            return {
                'success': True,
                'status': action,
                'message': message,
                'user_path': str(user_path),
                'backup_path': str(backup_path),
            }
        except Exception as exc:
            self.logger.warning('Building-Blocks-Synchronisation konnte nicht abgeschlossen werden: %s', exc, exc_info=True)
            return {
                'success': False,
                'status': 'error',
                'error': str(exc),
                'user_path': str(user_path),
                'backup_path': str(backup_path),
            }

    def update_building_blocks_template(self, font_name=None, font_size_word=None):
        """Optionales, isoliertes Patchen einer vorhandenen Building-Blocks-Vorlage.

        Falls keine passende Datei gefunden wird, bleibt das Verhalten komplett
        unverändert und die normalen Office-Templates werden nicht verändert.
        """
        fn = str(font_name or 'Arial').strip()
        fsw = int(font_size_word or 11)
        results = {}
        for candidate in self._get_building_blocks_candidates():
            if not candidate.exists():
                continue
            try:
                ok = self.safe_processor.update_word_building_blocks_xml(candidate, fn, fsw)
                results[candidate.name] = ok
                if ok:
                    self.logger.info("Building-Blocks-Datei erfolgreich angepasst: %s", candidate)
                else:
                    self.logger.warning("Building-Blocks-Datei konnte nicht angepasst werden: %s", candidate)
            except Exception as exc:
                self.logger.warning("Building-Blocks-Datei %s fehlerhaft: %s", candidate, exc)
                results[candidate.name] = False
        return results

    def _select_font_specific_templates(self, font_name, font_size_word, font_size_excel, font_size_outlook=12):
        """Verwendet vorbereitete, schrift- und größenbezogene Kopiervorlagen."""
        standard_dir = self.app_dir / "data" / "Datei-Vorlagen" / "Sonstiges" / "Standards"
        aliases = {
            "Futura Cyrillic": "Futura",
            "PT Sans Narrow": "PT Sans",
        }
        template_font = aliases.get(font_name, font_name)

        self.source_templates = dict(self._generic_source_templates)

        def size_text(value):
            try:
                numeric = float(value)
                return str(int(numeric)) if numeric.is_integer() else str(numeric).rstrip("0").rstrip(".")
            except (TypeError, ValueError):
                return str(value)

        word_size = size_text(font_size_word)
        outlook_size = size_text(font_size_outlook)
        excel_size = size_text(font_size_excel)
        candidates = {
            "normal_dotm": standard_dir / f"Normal-{template_font}-{word_size}.dotm",
            "normal_email_dotm": standard_dir / f"NormalEmail-{template_font}-{outlook_size}.dotm",
            "mappe_xltx": standard_dir / f"Mappe-{template_font}-{excel_size}.xltx",
        }
        for key, candidate in candidates.items():
            if candidate.is_file():
                self.source_templates[key] = candidate
                self.logger.info("Verwende Kopiervorlage: %s", candidate.name)
            else:
                self.logger.warning(
                    "Keine benannte Kopiervorlage für %s gefunden (%s); generische Vorlage bleibt Fallback.",
                    key,
                    candidate.name,
                )

    def update_font_in_templates(
        self,
        font_name=None,
        font_size_word=None,
        font_size_outlook=None,
        font_size_excel=None,
        corporate_design="INN-tegrativ",
        skip_excel_com=False,
        allow_com_fallback=False,
        **kwargs,
    ):
        """
        Setzt Schriftart und -größe in allen Templates.
        Bevorzugt XML-basierte Anpassung (kein COM, kein Bitness-Problem).
        COM als Fallback (nur wenn XML fehlschlägt und nicht im EXE-Modus).
        """
        import sys
        frozen = getattr(sys, 'frozen', False)
        result = {}
        fn = font_name or 'Arial'
        fsw = font_size_word or 11
        fso = font_size_outlook or 12
        fse = font_size_excel or 10
        self._select_font_specific_templates(fn, fsw, fse, fso)

        # Quelldateien niemals direkt verändern. Die ausgewählten Kopiervorlagen
        # werden in ein temporäres Arbeitsverzeichnis kopiert und ausschließlich
        # dort verarbeitet. copy_templates_to_user() übernimmt danach nur diese
        # validierten Arbeitskopien.
        if self._working_template_dir is not None:
            shutil.rmtree(self._working_template_dir, ignore_errors=True)
        self._working_template_dir = Path(tempfile.mkdtemp(prefix="pcconfig-templates-"))
        working_sources = {}

        # Optional: vorhandene Building-Blocks-Dateien separat patchen.
        # Keine bestehende Funktion wird dadurch ersetzt; wenn keine Datei
        # gefunden wird, bleibt das Ergebnis leer und der normale Flow läuft
        # unverändert weiter.
        building_blocks_result = self.update_building_blocks_template(fn, fsw)
        result['building_blocks'] = building_blocks_result
        for key, source_path in self.source_templates.items():
            if source_path.exists():
                working_path = self._working_template_dir / source_path.name
                shutil.copy2(source_path, working_path)
                working_sources[key] = working_path
        self.source_templates = working_sources
        self.logger.info("Verarbeite Vorlagen ausschließlich in temporären Kopien: %s", self._working_template_dir)

        # Word Normal.dotm
        src = self.source_templates.get('normal_dotm')
        if src and src.exists():
            try:
                # Benannte Normal-*.dotm-Dateien sind bereits vollständig
                # vorbereitete Word-Kopiervorlagen. Besonders Normal.dotm kann
                # VBA-Bestandteile enthalten; ein erneutes Serialisieren von
                # styles.xml kann Word anschließend zu einer Reparatur zwingen.
                # Daher diese Kopien nicht erneut per XML umschreiben.
                prepared = src.name.lower().startswith('normal-')
                prepared_info = self._read_word_font_info_from_template(src) if prepared else None
                prepared_matches = bool(
                    prepared_info
                    and self._normalize_font_name(prepared_info.get('font_name')) == self._normalize_font_name(fn)
                    and self._size_matches(prepared_info.get('font_size'), fsw)
                )
                ok = (
                    True
                    if prepared_matches
                    else self.safe_processor.update_word_template_xml(src, fn, fsw)
                )
                if prepared_matches:
                    self.logger.info("Word-Kopiervorlage bytegenau übernommen: %s", src.name)
                elif prepared:
                    self.logger.warning(
                        "Vorbereitete Word-Kopiervorlage %s enthielt abweichende Defaults; XML-Korrektur auf %s %spt durchgeführt.",
                        src.name,
                        fn,
                        fsw,
                    )
                if ok:
                    theme_path = self._theme_path(corporate_design, fn)
                    ok = self.safe_processor.apply_corporate_theme(
                        src, theme_path, "word/theme/theme1.xml", corporate_design
                    )
                    if ok:
                        self.logger.info("Word-Corporate-Theme mit Scheme-Farben übernommen: %s", theme_path.name)
                if not ok and allow_com_fallback and not frozen:
                    self.logger.info("XML-Fallback auf COM für Normal.dotm")
                    ok = self.safe_processor.update_word_template_safely(src, fn, fsw)
                result['normal_dotm'] = ok
            except Exception as e:
                self.logger.error(f"Fehler bei Normal.dotm-Anpassung: {e}")
                result['normal_dotm'] = False

        # Excel Mappe.xltx
        src = self.source_templates.get('mappe_xltx')
        if src and src.exists():
            try:
                ok = self.safe_processor.update_excel_template_xml(src, fn, fse)
                if ok:
                    ok = self.safe_processor.apply_corporate_theme(
                        src, self._theme_path(corporate_design, fn), "xl/theme/theme1.xml", corporate_design
                    )
                if not ok and allow_com_fallback and not frozen:
                    self.logger.info("XML-Fallback auf COM für Mappe.xltx")
                    ok = self.safe_processor.update_excel_template_safely(src, fn, fse)
                result['mappe_xltx'] = ok
            except Exception as e:
                self.logger.error(f"Fehler bei Mappe.xltx-Anpassung: {e}")
                result['mappe_xltx'] = False

        # Outlook NormalEmail.dotm
        if 'normal_email_dotm' in self.source_templates and self.source_templates['normal_email_dotm'].exists():
            try:
                email_source = self.source_templates['normal_email_dotm']
                prepared = email_source.name.lower().startswith('normalemail-')
                prepared_info = self._read_word_font_info_from_template(email_source) if prepared else None
                prepared_matches = bool(
                    prepared_info
                    and self._normalize_font_name(prepared_info.get('font_name')) == self._normalize_font_name(fn)
                    and self._size_matches(prepared_info.get('font_size'), fso)
                )
                ok = (
                    True
                    if prepared_matches
                    else self.safe_processor.update_word_template_xml(
                        email_source,
                        fn,
                        fso,
                        patch_theme_fonts=True,
                    )
                )
                if prepared_matches:
                    self.logger.info("Outlook-Kopiervorlage bytegenau übernommen: %s", email_source.name)
                elif prepared:
                    self.logger.warning(
                        "Vorbereitete Outlook-Kopiervorlage %s enthielt abweichende Defaults; XML-Korrektur auf %s %spt durchgeführt.",
                        email_source.name,
                        fn,
                        fso,
                    )
                if ok:
                    theme_path = self._theme_path(corporate_design, fn)
                    ok = self.safe_processor.apply_corporate_theme(
                        email_source, theme_path, "word/theme/theme1.xml", corporate_design
                    )
                    if ok:
                        self.logger.info("Outlook-Corporate-Theme mit Scheme-Farben übernommen: %s", theme_path.name)
                result['normal_email_dotm'] = ok
                # Nach Anpassung: Font auslesen und loggen
                if not ok and allow_com_fallback and not frozen:
                    self.logger.info("XML-Fallback auf COM für NormalEmail.dotm")
                    ok = self.safe_processor.update_word_template_safely(
                        email_source, fn, fso
                    )
                result['normal_email_dotm'] = ok
            except Exception as e:
                self.logger.error(f"Fehler bei NormalEmail.dotm-Anpassung: {e}")
                result['normal_email_dotm'] = False
        return result

    def _theme_path(self, design, font_name):
        prefixes = {'INN-tegrativ': 'Design_INN-tegrativ-', 'DBK': 'Design_DBK-', 'Careli': 'Design_Careli-'}
        folders = {'INN-tegrativ': 'Designs_INN-tegrativ', 'DBK': 'Designs_DBK', 'Careli': 'Designs_Careli'}
        if design not in prefixes:
            design = 'INN-tegrativ'
        # Die Fontauswahl kann detailliertere Familiennamen enthalten als die
        # vorbereiteten Office-Themes (z. B. Futura Cyrillic -> Futura).
        theme_font_name = {
            'Futura Cyrillic': 'Futura',
            'PT Sans Narrow': 'PT Sans',
        }.get(str(font_name), str(font_name))
        return self.app_dir / 'data' / 'Datei-Vorlagen' / 'Sonstiges' / folders[design] / f'{prefixes[design]}{theme_font_name}.thmx'

    def _modify_excel_template_via_powershell(self, template_path, font_name, font_size):
        """PowerShell-Fallback für Excel-Templates (setzt Schriftart und -größe via Skript)."""
        import subprocess
        from pathlib import Path
        ps_script = Path(__file__).parent / "set_excel_template_font.ps1"
        if not ps_script.exists():
            self.logger.error(f"PowerShell-Skript für Excel nicht gefunden: {ps_script}")
            return False
        cmd = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", str(ps_script),
            "-TemplatePath", str(template_path),
            "-FontName", str(font_name),
            "-FontSize", str(font_size)
        ]
        self.logger.info(f"Starte PowerShell-Fallback für Excel: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            stdout = result.stdout.strip() if result.stdout else "(keine Ausgabe)"
            stderr = result.stderr.strip() if result.stderr else "(keine Fehlerausgabe)"
            if result.returncode == 0:
                self.logger.info(f"PowerShell-Fallback für Excel erfolgreich: {stdout}")
                return True
            else:
                self.logger.error(f"PowerShell-Fallback für Excel fehlgeschlagen: {stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Fehler beim PowerShell-Fallback für Excel: {e}")
            return False

    def update_excel_template_safely(self, template_path, font_name, font_size):
        """Setzt die Schriftart und -größe in einer Excel-Vorlage (xltx) – direkt, ohne Umweg. Löscht ggf. Mappe.xlsx im Zielverzeichnis und kopiert Mappe.xltx explizit dorthin."""
        import subprocess
        import os
        import glob
        import sys
        from pathlib import Path
        procs = ["EXCEL.EXE", "WINWORD.EXE", "OUTLOOK.EXE"]
        creationflags = 0x08000000 if sys.platform == "win32" else 0
        for proc in procs:
            try:
                self.logger.info(f"Beende ggf. laufenden Prozess: {proc}")
                subprocess.run(["taskkill", "/IM", proc, "/F"], check=False, capture_output=True, creationflags=creationflags)
            except Exception as e:
                self.logger.warning(f"Konnte {proc} nicht beenden: {e}")
        # Vor dem Speichern: Alle Mappe*.xlsx im Zielverzeichnis löschen
        xlstart = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART"
        try:
            for f in glob.glob(str(xlstart / "Mappe*.xlsx")):
                try:
                    os.remove(f)
                    self.logger.info(f"Alte Datei im Zielverzeichnis gelöscht: {f}")
                except Exception as e:
                    self.logger.warning(f"Konnte {f} nicht löschen: {e}")
        except Exception as e:
            self.logger.warning(f"Fehler beim Löschen von Mappe*.xlsx: {e}")
        try:
            import win32com.client
            import pythoncom
            self.logger.info(f"Öffne Excel-Template über COM: {template_path} | Font: {font_name} | Size: {font_size}")
            pythoncom.CoInitialize()
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            # Fenster außerhalb des sichtbaren Bereichs positionieren (verhindert Aufblitzen)
            try:
                excel.WindowState = -2  # xlMinimized
                excel.Top = -10000
                excel.Left = -10000
            except Exception:
                pass
            wb = excel.Workbooks.Open(str(template_path), ReadOnly=False)
            for sheet in wb.Worksheets:
                try:
                    self.logger.debug(f"Setze Font für Blatt: {sheet.Name}")
                    sheet.Cells.Font.Name = font_name
                    sheet.Cells.Font.Size = font_size
                except Exception as sheet_error:
                    self.logger.error(f"Fehler beim Setzen des Fonts für Blatt {sheet.Name}: {sheet_error}")
            wb.SaveAs(str(template_path), FileFormat=52)  # 52 = xlOpenXMLTemplate
            wb.Close(False)
            excel.Quit()
            pythoncom.CoUninitialize()
            self.logger.info(f"Excel-Template erfolgreich modifiziert: {template_path}")
            # Nach Anpassung: Mappe.xlsx im Zielverzeichnis löschen, falls vorhanden
            xlstart = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART"
            mappe_xlsx = xlstart / "Mappe.xlsx"
            try:
                for f in glob.glob(str(xlstart / "Mappe*.xlsx")):
                    try:
                        os.remove(f)
                        self.logger.info(f"Alte Datei im Zielverzeichnis gelöscht: {f}")
                    except Exception as e:
                        self.logger.warning(f"Konnte {f} nicht löschen: {e}")
            except Exception as e:
                self.logger.warning(f"Fehler beim Löschen von Mappe*.xlsx: {e}")
            # Nach Anpassung: Mappe.xltx ins Benutzerverzeichnis kopieren
            try:
                target = xlstart / "Mappe.xltx"
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                from shutil import copy2
                copy2(template_path, target)
                self.logger.info(f"Mappe.xltx ins Benutzerverzeichnis kopiert: {target}")
            except Exception as e:
                self.logger.error(f"Fehler beim Kopieren von Mappe.xltx ins Benutzerverzeichnis: {e}")
            return True
        except Exception as e:
            self.logger.error(f"Fehler bei Excel COM-Automation für {template_path} (Font: {font_name}, Size: {font_size}): {e}")
            return False
    
    def copy_templates_to_user(self):
        """Kopiert Standard-Templates ins Benutzerprofil. Gibt Status-Dict zurück."""
        import subprocess
        # Vor dem Kopieren: Alle WINWORD.EXE-Prozesse beenden
        try:
            subprocess.run(["taskkill", "/IM", "WINWORD.EXE", "/F"], check=False, capture_output=True)
            self.logger.info("Alle WINWORD.EXE-Prozesse wurden vor dem Kopieren beendet.")
        except Exception as e:
            self.logger.warning(f"Konnte WINWORD.EXE nicht beenden: {e}")

        results = {}

        def copy_validated(source_path, target_path):
            with zipfile.ZipFile(source_path, "r") as archive:
                if archive.testzip() is not None:
                    raise ValueError(f"Beschädigte Office-Kopie: {source_path}")
            target_path = Path(target_path)
            temporary_target = target_path.with_name(target_path.name + ".pckconfig-copy.tmp")
            try:
                shutil.copy2(str(source_path), str(temporary_target))
                with zipfile.ZipFile(temporary_target, "r") as archive:
                    if archive.testzip() is not None:
                        raise ValueError(f"Beschädigte Zielkopie: {temporary_target}")
                os.replace(temporary_target, target_path)
            finally:
                if temporary_target.exists():
                    temporary_target.unlink()

        try:
            for template_key, source_path in self.source_templates.items():
                target_path = self.target_paths.get(template_key)
                if target_path is None:
                    self.logger.error(f"Kein Zielpfad für Template-Key: {template_key}")
                    results[template_key] = False
                    continue
                if not source_path.exists():
                    self.logger.warning(f"Quelldatei nicht gefunden: {source_path}")
                    results[template_key] = False
                    continue
                max_retries = 5
                for attempt in range(1, max_retries + 1):
                    try:
                        target_path = Path(target_path)
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        copy_validated(source_path, target_path)
                        self.logger.info(f"Validiert kopiert: {source_path} -> {target_path}")
                        results[template_key] = True
                        break
                    except Exception as e:
                        self.logger.error(f"Fehler beim Kopieren {source_path} -> {target_path} (Versuch {attempt}/{max_retries}): {e}")
                        results[template_key] = False
                        if attempt < max_retries:
                            time.sleep(2)
                else:
                    self.logger.error(f"Konnte {source_path} nach {max_retries} Versuchen nicht kopieren.")

            # Zusätzliche Excel-Vorlage: book.xltx aus Mappe.xltx ableiten
            mappe_target = self.target_paths.get('mappe_xltx')
            book_target = self.target_paths.get('book_xltx')
            if mappe_target and book_target:
                if results.get('mappe_xltx') and Path(mappe_target).exists():
                    try:
                        Path(book_target).parent.mkdir(parents=True, exist_ok=True)
                        copy_validated(mappe_target, book_target)
                        self.logger.info(f"Zusatzvorlage kopiert: {mappe_target} -> {book_target}")
                        results['book_xltx'] = True
                    except Exception as e:
                        self.logger.error(f"Fehler beim Kopieren der Zusatzvorlage {mappe_target} -> {book_target}: {e}")
                        results['book_xltx'] = False
                else:
                    self.logger.warning("Zusatzvorlage book.xltx übersprungen: Mappe.xltx wurde nicht erfolgreich kopiert.")
                    results['book_xltx'] = False
            return results
        finally:
            if self._working_template_dir is not None:
                shutil.rmtree(self._working_template_dir, ignore_errors=True)
                self._working_template_dir = None
            self.source_templates = dict(self._generic_source_templates)
