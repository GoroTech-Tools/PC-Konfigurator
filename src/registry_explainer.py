"""
Registry-Konfigurationen mit Erläuterungen.

Dieses Modul enthält zentrale Beschreibungen der Registry-Einstellungen,
die vom PC-Konfigurator verwendet werden.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RegistrySettingInfo:
    """Informationen über eine Registry-Einstellung."""

    key_path: str
    value_name: str
    value_type: str
    default_value: Any
    description: str
    impact: str
    category: str
    office_versions: List[str]


class RegistryExplainer:
    """Klasse zur Erläuterung von Registry-Einstellungen."""

    def __init__(self):
        self.settings = self._load_all_settings()

    def _load_all_settings(self) -> Dict[str, RegistrySettingInfo]:
        settings: Dict[str, RegistrySettingInfo] = {}
        settings.update(self._get_word_settings())
        settings.update(self._get_excel_settings())
        settings.update(self._get_general_office_settings())
        return settings

    def _get_word_settings(self) -> Dict[str, RegistrySettingInfo]:
        return {
            "word_correct_initial_caps": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="CorrectCapsLock",
                value_type="REG_DWORD",
                default_value=0,
                description="Korrigiert automatisch zwei Großbuchstaben am Wortanfang.",
                impact="Wenn deaktiviert, werden Wörter wie 'DEr' nicht automatisch korrigiert.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"],
            ),
            "word_correct_sentence_caps": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="CorrectSentenceCaps",
                value_type="REG_DWORD",
                default_value=0,
                description="Beginnt Sätze automatisch mit Großbuchstaben.",
                impact="Wenn deaktiviert, bleibt die automatische Großschreibung aus.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"],
            ),
            "word_auto_bullets": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="AutoFormatAsYouTypeApplyBulletedLists",
                value_type="REG_DWORD",
                default_value=0,
                description="Automatische Aufzählungen beim Tippen.",
                impact="Wenn deaktiviert, werden Zeichen wie '-' nicht automatisch zu Aufzählungen.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"],
            ),
            "word_auto_numbering": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="AutoFormatAsYouTypeApplyNumberedLists",
                value_type="REG_DWORD",
                default_value=0,
                description="Automatische Nummerierung beim Tippen.",
                impact="Wenn deaktiviert, werden Zahlen am Zeilenanfang nicht automatisch umgewandelt.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"],
            ),
            "word_smart_quotes": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="AutoFormatAsYouTypeReplaceQuotes",
                value_type="REG_DWORD",
                default_value=1,
                description="Gerade Anführungszeichen durch typografische ersetzen.",
                impact="Wenn aktiviert, werden \" und ' in typografische Anführungszeichen umgewandelt.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"],
            ),
            "word_developer_tools": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="DeveloperTools",
                value_type="REG_DWORD",
                default_value=1,
                description="Aktiviert die Entwicklertools in Word.",
                impact="Zeigt die Registerkarte 'Entwicklertools' an.",
                category="Word - Benutzeroberfläche",
                office_versions=["15.0", "16.0"],
            ),
            "word_disable_start_screen": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\General",
                value_name="DisableBootToOfficeStart",
                value_type="REG_DWORD",
                default_value=1,
                description="Deaktiviert den Word-Startbildschirm beim Programmstart.",
                impact="Word startet direkt mit einem neuen leeren Dokument statt der Startseite.",
                category="Word - Benutzeroberfläche",
                office_versions=["15.0", "16.0"],
            ),
            "word_ruler": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="Ruler",
                value_type="REG_DWORD",
                default_value=1,
                description="Zeigt das Lineal in Word an.",
                impact="Erleichtert Einrückungen, Tabstopps und Seitenränder.",
                category="Word - Ansicht",
                office_versions=["15.0", "16.0"],
            ),
            "word_show_all_formatting": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="ShowAllFormatting",
                value_type="REG_DWORD",
                default_value=1,
                description="Zeigt Formatierungszeichen an.",
                impact="Macht Leerzeichen, Tabs und Absatzmarken sichtbar.",
                category="Word - Formatierung",
                office_versions=["15.0", "16.0"],
            ),
            "word_table_gridlines": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="VisiDrawTableDrs",
                value_type="REG_DWORD",
                default_value=1,
                description="Zeigt Tabellengitternetzlinien an.",
                impact="Erleichtert das Bearbeiten von Tabellen.",
                category="Word - Tabellen",
                office_versions=["15.0", "16.0"],
            ),
            "word_doc_path": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="DOC-PATH",
                value_type="REG_SZ",
                default_value="",
                description="Standardpfad für Word-Dokumente.",
                impact="Bestimmt den vorgeschlagenen Speicherort in Word.",
                category="Word - Dateipfade",
                office_versions=["15.0", "16.0"],
            ),
            "word_default_font": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Data",
                value_name="Default Font",
                value_type="REG_SZ",
                default_value="Aptos",
                description="Standard-Schriftart für neue Word-Dokumente.",
                impact="Neue Dokumente verwenden diese Schriftart.",
                category="Word - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "word_default_font_size": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Data",
                value_name="Default Font Size",
                value_type="REG_DWORD",
                default_value=11,
                description="Standard-Schriftgröße für neue Word-Dokumente.",
                impact="Neue Dokumente verwenden diese Schriftgröße.",
                category="Word - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "word_dot_path": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="DOT-PATH",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Verzeichnis der Word-Benutzervorlagen (enthält u. a. Normal.dotm). "
                    "Leer = Word nutzt das Standard-Vorlagenverzeichnis "
                    "(%APPDATA%\\Microsoft\\Templates)."
                ),
                impact=(
                    "Word sucht Normal.dotm in diesem Verzeichnis. "
                    "Falsch gesetzt, wird Normal.dotm ignoriert und Word zeigt "
                    "die werksseitige Schriftart."
                ),
                category="Word - Datei-Vorlagen",
                office_versions=["15.0", "16.0"],
            ),
            "word_startup_path": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="STARTUP-PATH",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Word-Startverzeichnis. Add-Ins und Vorlagen in diesem Ordner "
                    "werden beim Programmstart automatisch geladen."
                ),
                impact=(
                    "Leer = Word nutzt den Standard-Startordner. "
                    "Beim Einsatz eigener Makro-Vorlagen muss dieses Verzeichnis korrekt zeigen."
                ),
                category="Word - Datei-Vorlagen",
                office_versions=["15.0", "16.0"],
            ),
            "word_font_override": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="Font",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Schriftart, die Word in der Schriftauswahl-Dropdownliste bei neuen Dokumenten "
                    "vorschlägt. Dieser Wert übersteuert die in der Normal.dotm gespeicherte Schrift."
                ),
                impact=(
                    "Muss auf die gewünschte Schriftart gesetzt sein. Fehlt dieser Eintrag oder "
                    "ist er falsch, zeigt Word beim Erstellen neuer Dokumente die falsche Schrift."
                ),
                category="Word - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "word_font_substitutes": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="Fontsubstitutes",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Schriftartersetzungstabelle (Format: 'Aptos=Arial;Calibri=Arial'). "
                    "Enthält dieser Eintrag Ersetzungen, zeigt Word andere Schriften als "
                    "in der Vorlage definiert – unabhängig von Normal.dotm."
                ),
                impact=(
                    "Muss geleert werden. Einträge wie 'Aptos=Arial' verhindern die Anzeige der "
                    "konfigurierten Schriftart, selbst wenn Normal.dotm korrekt konfiguriert ist."
                ),
                category="Word - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "word_personal_templates": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="PersonalTemplates",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Standardspeicherort für persönliche Word-Vorlagen. Wird in "
                    "'Datei > Neu > Persönlich' angezeigt. Ab Office 2013 der empfohlene "
                    "Weg, eigene Vorlagen zugänglich zu machen (ersetzt teilweise DOT-PATH)."
                ),
                impact=(
                    "Leer = Word zeigt keine persönlichen Vorlagen unter 'Neu > Persönlich'. "
                    "Korrekt gesetzt ermöglicht direkten Zugriff auf Vorlagen aus Office heraus."
                ),
                category="Word - Datei-Vorlagen",
                office_versions=["15.0", "16.0"],
            ),
        }

    def _get_excel_settings(self) -> Dict[str, RegistrySettingInfo]:
        return {
            "excel_path": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                value_name="EXCEL-PATH",
                value_type="REG_SZ",
                default_value="",
                description="Standardpfad für Excel-Dateien.",
                impact="Bestimmt den vorgeschlagenen Speicherort in Excel.",
                category="Excel - Dateipfade",
                office_versions=["15.0", "16.0"],
            ),
            "excel_autosave_interval": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                value_name="AutoSaveInterval",
                value_type="REG_DWORD",
                default_value=5,
                description="Intervall für AutoWiederherstellen in Minuten.",
                impact="Verringert Datenverlust bei Abstürzen.",
                category="Excel - Autowiederherstellen",
                office_versions=["15.0", "16.0"],
            ),
            "excel_default_font": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Data",
                value_name="Default Font",
                value_type="REG_SZ",
                default_value="Aptos",
                description="Standard-Schriftart für neue Arbeitsmappen.",
                impact="Neue Arbeitsmappen verwenden diese Schriftart.",
                category="Excel - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "excel_default_font_size": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Data",
                value_name="Default Font Size",
                value_type="REG_DWORD",
                default_value=10,
                description="Standard-Schriftgröße für neue Arbeitsmappen.",
                impact="Neue Arbeitsmappen verwenden diese Schriftgröße.",
                category="Excel - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "excel_xlstart_info": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                value_name="AltStartupPath",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Zusätzliches Excel-Startverzeichnis (XLSTART-Ergänzung). "
                    "Excel lädt beim Start alle Dateien aus dem Standard-XLSTART-Ordner "
                    "(%APPDATA%\\Microsoft\\Excel\\XLSTART) sowie diesem Pfad. "
                    "Mappe.xltx im XLSTART-Ordner definiert die Arbeitsmappenvorlage."
                ),
                impact=(
                    "Leer = Excel verwendet nur den Standard-XLSTART-Ordner. "
                    "Mappe.xltx wird von dort geladen. Fehlt die Datei, "
                    "nutzt Excel die interne Standardschrift (meist Calibri)."
                ),
                category="Excel - Datei-Vorlagen",
                office_versions=["15.0", "16.0"],
            ),
            "excel_font_override": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                value_name="Font",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Schriftart und -größe, die Excel in der Schriftauswahl vorschlägt. "
                    "Format: 'Schriftartname,Größe' (z. B. 'Aptos,10'). "
                    "Steuert die im Ribbon angezeigte Standardschriftart."
                ),
                impact=(
                    "Muss auf 'Schriftartname,Größe' gesetzt sein. Sonst zeigt Excel beim "
                    "Start über das Startmenü eine abweichende Schriftart in der Werkzeugleiste."
                ),
                category="Excel - Schriftarten",
                office_versions=["15.0", "16.0"],
            ),
            "excel_personal_templates": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                value_name="PersonalTemplates",
                value_type="REG_SZ",
                default_value="",
                description=(
                    "Standardspeicherort für persönliche Excel-Vorlagen. Wird in "
                    "'Datei > Neu > Persönlich' angezeigt. Ab Office 2013 der empfohlene "
                    "Weg, eigene Vorlagen zugänglich zu machen."
                ),
                impact=(
                    "Leer = Excel zeigt keine persönlichen Vorlagen unter 'Neu > Persönlich'. "
                    "Korrekt gesetzt ermöglicht direkten Zugriff auf Vorlagen aus Excel heraus."
                ),
                category="Excel - Datei-Vorlagen",
                office_versions=["15.0", "16.0"],
            ),
        }

    def _get_general_office_settings(self) -> Dict[str, RegistrySettingInfo]:
        return {
            "office_first_run": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\General",
                value_name="ShownFilesNewUX",
                value_type="REG_DWORD",
                default_value=1,
                description="Überspringt die Willkommensseite beim ersten Start.",
                impact="Beschleunigt den Arbeitsbeginn.",
                category="Office - Allgemein",
                office_versions=["15.0", "16.0"],
            ),
            "office_customer_experience": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\QMEnable",
                value_name="CEIPEnable",
                value_type="REG_DWORD",
                default_value=0,
                description="Deaktiviert das Microsoft CEIP-Programm.",
                impact="Verbessert den Datenschutz.",
                category="Office - Datenschutz",
                office_versions=["15.0", "16.0"],
            ),
            "office_updates": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\OfficeUpdate",
                value_name="EnableAutomaticUpdates",
                value_type="REG_DWORD",
                default_value=1,
                description="Aktiviert automatische Office-Updates.",
                impact="Sicherheits- und Feature-Updates werden automatisch eingespielt.",
                category="Office - Updates",
                office_versions=["15.0", "16.0"],
            ),
            "windows_taskbar_alignment": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="TaskbarAl",
                value_type="REG_DWORD",
                default_value=0,
                description="Taskleiste linksbündig (0) oder zentriert (1).",
                impact="0 = linksbündig wie Windows 10, 1 = zentriert.",
                category="Windows - Taskleiste",
                office_versions=["15.0", "16.0"],
            ),
            "windows_hide_widgets": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="TaskbarDa",
                value_type="REG_DWORD",
                default_value=0,
                description="Widgets in der Taskleiste ausblenden.",
                impact="Blendet das Widgets-Icon aus.",
                category="Windows - Taskleiste",
                office_versions=["15.0", "16.0"],
            ),
            "windows_hide_searchbox": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="SearchboxTaskbarMode",
                value_type="REG_DWORD",
                default_value=0,
                description="Suchfeld in der Taskleiste ausblenden.",
                impact="0 = ausgeblendet, 1 = Symbol, 2 = Feld.",
                category="Windows - Taskleiste",
                office_versions=["15.0", "16.0"],
            ),
            "windows_explorer_show_extensions": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="HideFileExt",
                value_type="REG_DWORD",
                default_value=0,
                description="Dateiendungen im Explorer anzeigen.",
                impact="Erhöht Transparenz und Sicherheit beim Dateityp.",
                category="Windows - Explorer",
                office_versions=["15.0", "16.0"],
            ),
            "windows_explorer_show_hidden_items": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Hidden",
                value_type="REG_DWORD",
                default_value=1,
                description="Ausgeblendete Elemente im Explorer anzeigen.",
                impact="Versteckte Dateien und Ordner werden sichtbar.",
                category="Windows - Explorer",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_list_view": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_TrackProgs",
                value_type="REG_DWORD",
                default_value=1,
                description="Startmenü auf App-Liste/Listenansicht ausrichten (sofern vom Build unterstützt).",
                impact="Zeigt Programme stärker listenorientiert im Startbereich an.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_list_layout": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_Layout",
                value_type="REG_DWORD",
                default_value=1,
                description="Start-Layout auf Listen-/All-Apps-orientierte Ansicht setzen (Build-abhängig).",
                impact="Fördert eine listenorientierte Darstellung im Startmenü.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_show_documents": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_ShowDocuments",
                value_type="REG_DWORD",
                default_value=1,
                description="Ordner 'Dokumente' im Startmenü anzeigen (sofern vom Build unterstützt).",
                impact="Schnellzugriff auf Dokumente direkt über Start.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_track_documents": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_TrackDocs",
                value_type="REG_DWORD",
                default_value=1,
                description="Dokumente im Startbereich/Empfehlungen nachverfolgen und anzeigen (Build-abhängig).",
                impact="Erhöht Sichtbarkeit von Dokumenten im Startmenü-Kontext.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_show_downloads": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_ShowDownloads",
                value_type="REG_DWORD",
                default_value=1,
                description="Ordner 'Downloads' im Startmenü anzeigen (sofern vom Build unterstützt).",
                impact="Schnellzugriff auf Downloads direkt über Start.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_show_network": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_ShowNetwork",
                value_type="REG_DWORD",
                default_value=1,
                description="Symbol 'Netzwerk' im Startmenü anzeigen (sofern vom Build unterstützt).",
                impact="Erleichtert den Zugriff auf Netzwerkressourcen.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_show_file_explorer": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_ShowFileExplorer",
                value_type="REG_DWORD",
                default_value=1,
                description="Symbol 'Datei-Explorer' im Startmenü anzeigen (sofern vom Build unterstützt).",
                impact="Direkter Explorer-Zugriff über das Startmenü.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_show_settings": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_ShowSettings",
                value_type="REG_DWORD",
                default_value=1,
                description="Symbol 'Einstellungen' im Startmenü anzeigen (sofern vom Build unterstützt).",
                impact="Schneller Zugriff auf Windows-Einstellungen.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
            "windows_startmenu_show_power": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                value_name="Start_ShowPowerButton",
                value_type="REG_DWORD",
                default_value=1,
                description="Ein-/Aus-Symbol im Startmenü anzeigen (sofern vom Build unterstützt).",
                impact="Schneller Zugriff auf Herunterfahren/Neustart.",
                category="Windows - Startmenü",
                office_versions=["15.0", "16.0"],
            ),
        }

    def get_setting_by_name(self, setting_name: str) -> Optional[RegistrySettingInfo]:
        return self.settings.get(setting_name)

    def get_settings_by_category(self, category: str) -> List[RegistrySettingInfo]:
        return [setting for setting in self.settings.values() if setting.category.startswith(category)]

    def get_all_categories(self) -> List[str]:
        categories = {setting.category.split(" - ")[0] for setting in self.settings.values()}
        return sorted(categories)

    def format_registry_path(self, setting: RegistrySettingInfo, office_version: str = "16.0") -> str:
        return setting.key_path.replace("{version}", office_version)

    def get_full_registry_info(self, setting_name: str, office_version: str = "16.0") -> Dict[str, Any]:
        setting = self.get_setting_by_name(setting_name)
        if not setting:
            return {}

        return {
            "name": setting_name,
            "full_path": f"HKEY_CURRENT_USER\\{self.format_registry_path(setting, office_version)}",
            "value_name": setting.value_name,
            "value_type": setting.value_type,
            "default_value": setting.default_value,
            "description": setting.description,
            "impact": setting.impact,
            "category": setting.category,
            "office_versions": setting.office_versions,
        }

    def export_all_settings(self, office_version: str = "16.0") -> Dict[str, Any]:
        export_data = {
            "office_version": office_version,
            "settings_count": len(self.settings),
            "categories": self.get_all_categories(),
            "settings": {},
        }

        for name, setting in self.settings.items():
            if office_version in setting.office_versions:
                export_data["settings"][name] = self.get_full_registry_info(name, office_version)

        return export_data

    def validate_setting_value(self, setting_name: str, value: Any) -> bool:
        setting = self.get_setting_by_name(setting_name)
        if not setting:
            return False

        if setting.value_type == "REG_DWORD":
            return isinstance(value, int) and 0 <= value <= 4294967295
        if setting.value_type == "REG_SZ":
            return isinstance(value, str) and len(value) <= 260

        return False

    def check_gpo_office_theme(self, office_version: str = "16.0") -> Dict[str, Any]:
        """
        Prüft, ob eine Gruppenrichtlinie (GPO) ein Office-Design/Theme vorgibt.

        Office-GPOs schreiben in den 'Policies'-Zweig der Registry:
          HKCU\\SOFTWARE\\Policies\\Microsoft\\Office\\...
          HKLM\\SOFTWARE\\Policies\\Microsoft\\Office\\...

        Rückgabe (Dict):
          'gpo_active'        : bool   – True, wenn mind. eine relevante Richtlinie gefunden wurde
          'entries'           : list   – Liste der gefundenen Richtlinien-Einträge
          'checked_paths'     : list   – Alle durchsuchten Registry-Pfade
          'recommendation'    : str    – Handlungsempfehlung
        """
        import winreg

        # Registry-Pfade, in denen Office-Richtlinien für Themes stehen können
        policy_paths = [
            # Benutzerbezogene Richtlinien (HKCU)
            (winreg.HKEY_CURRENT_USER,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Common\\General"),
            (winreg.HKEY_CURRENT_USER,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Common\\Graphics"),
            (winreg.HKEY_CURRENT_USER,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Word\\Options"),
            (winreg.HKEY_CURRENT_USER,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Excel\\Options"),
            # Maschinenbezogene Richtlinien (HKLM)
            (winreg.HKEY_LOCAL_MACHINE,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Common\\General"),
            (winreg.HKEY_LOCAL_MACHINE,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Common\\Graphics"),
            (winreg.HKEY_LOCAL_MACHINE,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Word\\Options"),
            (winreg.HKEY_LOCAL_MACHINE,
             f"SOFTWARE\\Policies\\Microsoft\\Office\\{office_version}\\Excel\\Options"),
        ]

        # Werte, die auf eine Theme/Design-Richtlinie hindeuten
        theme_value_keywords = {
            "theme", "design", "font", "schrift", "template", "vorlage",
            "color", "farbe", "scheme", "style",
        }

        entries: list = []
        checked_paths: list = []
        hive_names = {
            winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
            winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
        }

        for hive, path in policy_paths:
            hive_name = hive_names.get(hive, str(hive))
            full_path = f"{hive_name}\\{path}"
            checked_paths.append(full_path)
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, data, reg_type = winreg.EnumValue(key, i)
                            name_lower = name.lower()
                            is_theme_related = any(
                                kw in name_lower for kw in theme_value_keywords
                            )
                            entries.append({
                                "path": full_path,
                                "name": name,
                                "data": data,
                                "type": reg_type,
                                "theme_related": is_theme_related,
                            })
                            i += 1
                        except OSError:
                            break  # Keine weiteren Werte
            except FileNotFoundError:
                pass  # Key existiert nicht – keine Richtlinie aktiv
            except PermissionError:
                checked_paths[-1] += " (kein Zugriff)"

        gpo_active = bool(entries)
        theme_entries = [e for e in entries if e["theme_related"]]

        if theme_entries:
            recommendation = (
                "Es wurden GPO-Einträge mit Theme-/Design-Bezug gefunden. "
                "Diese überschreiben möglicherweise die Template-Anpassungen. "
                "Bitte die IT-Abteilung/Gruppenrichtlinien-Verwaltung kontaktieren."
            )
        elif gpo_active:
            recommendation = (
                "Es wurden Office-Gruppenrichtlinien gefunden, aber keine "
                "eindeutigen Theme-Einträge. Die Richtlinien können die Schrift "
                "trotzdem indirekt beeinflussen."
            )
        else:
            recommendation = (
                "Keine Office-Gruppenrichtlinien für Themes/Designs gefunden. "
                "Falls das Problem weiterhin besteht, prüfen Sie das Theme-XML "
                "direkt in der Template-Datei."
            )

        return {
            "gpo_active": gpo_active,
            "theme_related_count": len(theme_entries),
            "all_entries_count": len(entries),
            "entries": entries,
            "checked_paths": checked_paths,
            "recommendation": recommendation,
        }