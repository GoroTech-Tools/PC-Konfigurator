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