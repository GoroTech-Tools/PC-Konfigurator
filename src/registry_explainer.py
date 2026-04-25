"""
Registry-Konfigurationen mit Erläuterungen
==========================================

Dieses Modul enthält detaillierte Beschreibungen aller Registry-Einstellungen
die vom PC-Konfigurator vorgenommen werden.
"""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class RegistrySettingInfo:
    """Informationen über eine Registry-Einstellung"""
    key_path: str
    value_name: str
    value_type: str
    default_value: Any
    description: str
    impact: str
    category: str
    office_versions: List[str]


class RegistryExplainer:
                # Typografische Anführungszeichen (Word)
                "word_smart_quotes": RegistrySettingInfo(
                    key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                    value_name="AutoFormatAsYouTypeReplaceQuotes",
                    value_type="REG_DWORD",
                    default_value=1,
                    description="Gerade Anführungszeichen durch typografische ersetzen (Autokorrektur)",
                    impact="Wenn aktiviert, werden gerade Anführungszeichen (\" und ') automatisch in typografische Anführungszeichen (“ ” und ‘ ’) umgewandelt.",
                    category="Word - Autokorrektur",
                    office_versions=["15.0", "16.0"]
                ),
    """Klasse zur Erläuterung von Registry-Einstellungen"""
    
    def __init__(self):
        self.settings = self._load_all_settings()
    
    def _load_all_settings(self) -> Dict[str, RegistrySettingInfo]:
        """Alle Registry-Einstellungen mit Beschreibungen laden"""
        
        settings = {}
        
        # Word-Einstellungen
        word_settings = self._get_word_settings()
        settings.update(word_settings)
        
        # Excel-Einstellungen
        excel_settings = self._get_excel_settings()
        settings.update(excel_settings)
        
        # Allgemeine Office-Einstellungen
        office_settings = self._get_general_office_settings()
        settings.update(office_settings)
        
        return settings
    
    def _get_word_settings(self) -> Dict[str, RegistrySettingInfo]:
        """Word-spezifische Registry-Einstellungen"""
        # Hinweise zu den Autokorrektur-Optionen:
        # Die meisten Autokorrektur-Optionen werden unter "Proofing" oder "AutoCorrect" gespeichert.
        # Die Registry-Pfade und Value-Namen können je nach Office-Version variieren.
        # Die folgenden Einstellungen gelten für Office 2013/2016/2019/365 (Version 15.0/16.0):
        return {
            # Zwei Großbuchstaben am Wortanfang korrigieren
            "word_correct_initial_caps": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="CorrectCapsLock",
                value_type="REG_DWORD",
                default_value=0,
                description="Korrigiert automatisch zwei Großbuchstaben am Wortanfang (Autokorrektur)",
                impact="Wenn deaktiviert, werden Wörter wie 'DEr' nicht automatisch zu 'Der' korrigiert.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"]
            ),

            # Jeden Satz mit einem Großbuchstaben beginnen
            "word_correct_sentence_caps": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="CorrectSentenceCaps",
                value_type="REG_DWORD",
                default_value=0,
                description="Beginnt jeden Satz automatisch mit einem Großbuchstaben (Autokorrektur)",
                impact="Wenn deaktiviert, wird der erste Buchstabe nach einem Punkt nicht automatisch groß geschrieben.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"]
            ),

            # Automatische Aufzählung
            "word_auto_bullets": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="AutoFormatAsYouTypeApplyBulletedLists",
                value_type="REG_DWORD",
                default_value=0,
                description="Automatische Umwandlung von Listenzeichen in Aufzählungen (Autokorrektur)",
                impact="Wenn deaktiviert, werden Listenzeichen wie '-' oder '*' nicht automatisch in Aufzählungen umgewandelt.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"]
            ),

            # Automatische Nummerierung
            "word_auto_numbering": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="AutoFormatAsYouTypeApplyNumberedLists",
                value_type="REG_DWORD",
                default_value=0,
                description="Automatische Umwandlung von Zahlen in nummerierte Listen (Autokorrektur)",
                impact="Wenn deaktiviert, werden Zahlen am Zeilenanfang nicht automatisch in nummerierte Listen umgewandelt.",
                category="Word - Autokorrektur",
                office_versions=["15.0", "16.0"]
            ),

            "word_developer_tools": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="DeveloperTools",
                value_type="REG_DWORD",
                default_value=1,
                description="Aktiviert die Entwicklertools in der Word-Menüleiste",
                impact="Zeigt die 'Entwicklertools'-Registerkarte in Word an, die Zugriff auf Makros, "
                       "Formular-Steuerelemente, XML-Zuordnung und Add-Ins bietet.",
                category="Word - Benutzeroberfläche",
                office_versions=["15.0", "16.0"]
            ),

            "word_ruler": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="Ruler",
                value_type="REG_DWORD", 
                default_value=1,
                description="Zeigt das Lineal in Word an",
                impact="Das horizontale Lineal wird standardmäßig im Word-Dokument angezeigt. "
                       "Erleichtert die Formatierung von Einrückungen, Tabstopps und Seitenrändern.",
                category="Word - Ansicht",
                office_versions=["15.0", "16.0"]
            ),

            "word_show_all_formatting": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="ShowAllFormatting",
                value_type="REG_DWORD",
                default_value=1,
                description="Zeigt alle Formatierungszeichen an",
                impact="Macht unsichtbare Zeichen wie Leerzeichen, Tabs, Absatzmarken und "
                       "Seitenumbrüche sichtbar. Hilfreich für die präzise Dokumentformatierung.",
                category="Word - Formatierung",
                office_versions=["15.0", "16.0"]
            ),

            "word_table_gridlines": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options", 
                value_name="VisiDrawTableDrs",
                value_type="REG_DWORD",
                default_value=1,
                description="Zeigt Tabellengitternetzlinien an",
                impact="Macht die Ränder von Tabellen sichtbar, auch wenn keine Rahmenlinien "
                       "definiert sind. Erleichtert die Tabellenbearbeitung.",
                category="Word - Tabellen",
                office_versions=["15.0", "16.0"]
            ),

            "word_doc_path": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Options",
                value_name="DOC-PATH",
                value_type="REG_SZ",
                default_value="",
                description="Standardpfad für Word-Dokumente",
                impact="Bestimmt den Standardordner, der beim Öffnen und Speichern von "
                       "Dokumenten angezeigt wird. Verbessert die Arbeitseffizienz.",
                category="Word - Dateipfade",
                office_versions=["15.0", "16.0"]
            ),

            "word_default_font": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Data",
                value_name="Default Font",
                value_type="REG_SZ",
                default_value="Aptos",
                description="Standard-Schriftart für neue Dokumente",
                impact="Neue Word-Dokumente verwenden automatisch diese Schriftart. "
                       "Sorgt für einheitliche Dokumentgestaltung.",
                category="Word - Schriftarten",
                office_versions=["15.0", "16.0"]
            ),

            "word_default_font_size": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Word\\Data",
                value_name="Default Font Size", 
                value_type="REG_DWORD",
                default_value=11,
                description="Standard-Schriftgröße für neue Dokumente",
                impact="Neue Word-Dokumente verwenden automatisch diese Schriftgröße. "
                       "Optimiert für gute Lesbarkeit und professionelles Erscheinungsbild.",
                category="Word - Schriftarten",
                office_versions=["15.0", "16.0"]
            )
        }
    
    def _get_excel_settings(self) -> Dict[str, RegistrySettingInfo]:
        """Excel-spezifische Registry-Einstellungen"""
        
        return {
            "excel_path": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                value_name="EXCEL-PATH", 
                value_type="REG_SZ",
                default_value="",
                description="Standardpfad für Excel-Dateien",
                impact="Bestimmt den Standardordner, der beim Öffnen und Speichern von "
                       "Excel-Arbeitsmappen angezeigt wird.",
                category="Excel - Dateipfade",
                office_versions=["15.0", "16.0"]
            ),
                # Autowiederherstellen-Informationen speichern alle fünf Minuten (Excel)
                "excel_autosave_interval": RegistrySettingInfo(
                    key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Options",
                    value_name="AutoSaveInterval",
                    value_type="REG_DWORD",
                    default_value=5,
                    description="Speichert Autowiederherstellen-Informationen alle fünf Minuten (Excel)",
                    impact="Reduziert Datenverlust bei Abstürzen. Excel speichert alle 5 Minuten eine Wiederherstellungsdatei.",
                    category="Excel - Autowiederherstellen",
                    office_versions=["15.0", "16.0"]
                ),
            
            "excel_default_font": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Data",
                value_name="Default Font",
                value_type="REG_SZ", 
                default_value="Aptos",
                description="Standard-Schriftart für neue Arbeitsmappen",
                impact="Neue Excel-Arbeitsmappen verwenden automatisch diese Schriftart. "
                       "Sorgt für einheitliche Darstellung in Tabellen.",
                category="Excel - Schriftarten",
                office_versions=["15.0", "16.0"]
            ),
            
            "excel_default_font_size": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Excel\\Data",
                value_name="Default Font Size",
                value_type="REG_DWORD",
                default_value=10,
                description="Standard-Schriftgröße für neue Arbeitsmappen",
                impact="Neue Excel-Arbeitsmappen verwenden automatisch diese Schriftgröße. "
                       "Optimiert für maximale Datenanzeige bei guter Lesbarkeit.",
                category="Excel - Schriftarten", 
                office_versions=["15.0", "16.0"]
            )
        }
    
    def _get_general_office_settings(self) -> Dict[str, RegistrySettingInfo]:
        """Allgemeine Office- und Windows-Einstellungen"""
        settings = {
                        # Weitere Windows-Einstellungen
                        "windows_taskbar_alignment": RegistrySettingInfo(
                            key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                            value_name="TaskbarAl",
                            value_type="REG_DWORD",
                            default_value=0,
                            description="Taskleiste linksbündig (0) oder zentriert (1)",
                            impact="0 = linksbündig wie bei Windows 10, 1 = zentriert wie Windows 11-Standard.",
                            category="Windows - Taskleiste",
                            office_versions=["15.0", "16.0"]
                        ),
                        "windows_hide_widgets": RegistrySettingInfo(
                            key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                            value_name="TaskbarDa",
                            value_type="REG_DWORD",
                            default_value=0,
                            description="Widgets-Schaltfläche in der Taskleiste ausblenden (0=ausgeblendet, 1=angezeigt)",
                            impact="Blendet das Widgets-Icon in der Taskleiste aus.",
                            category="Windows - Taskleiste",
                            office_versions=["15.0", "16.0"]
                        ),
                        "windows_hide_searchbox": RegistrySettingInfo(
                            key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                            value_name="SearchboxTaskbarMode",
                            value_type="REG_DWORD",
                            default_value=0,
                            description="Suchfeld in der Taskleiste ausblenden (0=ausgeblendet, 1=Suchsymbol, 2=Suchfeld)",
                            impact="0 = ausgeblendet, 1 = nur Symbol, 2 = Suchfeld sichtbar.",
                            category="Windows - Taskleiste",
                            office_versions=["15.0", "16.0"]
                        ),
            "office_first_run": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\General",
                value_name="ShownFilesNewUX",
                value_type="REG_DWORD",
                default_value=1,
                description="Überspringt die Willkommensseite bei erstem Start",
                impact="Verhindert, dass bei jedem ersten Programmstart die Willkommensseite angezeigt wird. Beschleunigt den Arbeitsbeginn.",
                category="Office - Allgemein",
                office_versions=["15.0", "16.0"]
            ),
            "office_customer_experience": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\QMEnable",
                value_name="CEIPEnable",
                value_type="REG_DWORD",
                default_value=0,
                description="Deaktiviert das Programm zur Verbesserung der Benutzerfreundlichkeit",
                impact="Verhindert, dass Nutzungsdaten an Microsoft gesendet werden. Verbessert den Datenschutz.",
                category="Office - Datenschutz",
                office_versions=["15.0", "16.0"]
            ),
            "office_updates": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Office\\{version}\\Common\\OfficeUpdate",
                value_name="EnableAutomaticUpdates",
                value_type="REG_DWORD", 
                default_value=1,
                description="Aktiviert automatische Office-Updates",
                impact="Office wird automatisch mit Sicherheits- und Feature-Updates versorgt. Wichtig für Sicherheit und Stabilität.",
                category="Office - Updates",
                office_versions=["15.0", "16.0"]
            ),
            # Beispielhafte Windows-Einstellung
            "windows_explorer_show_extensions": RegistrySettingInfo(
                key_path="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\Advanced",
                value_name="HideFileExt",
                value_type="REG_DWORD",
                default_value=0,
                description="Dateinamenerweiterungen für bekannte Dateitypen anzeigen",
                impact="Wenn aktiviert, werden Dateiendungen wie .txt, .docx, .xlsx im Explorer angezeigt.",
                category="Windows - Explorer",
                office_versions=["15.0", "16.0"]
            )
        }
        return settings
    
    from typing import Optional
    def get_setting_by_name(self, setting_name: str) -> Optional[RegistrySettingInfo]:
        """Registry-Einstellung anhand des Namens abrufen"""
        return self.settings.get(setting_name)
    
    def get_settings_by_category(self, category: str) -> List[RegistrySettingInfo]:
        """Alle Einstellungen einer Kategorie abrufen"""
        return [setting for setting in self.settings.values() 
                if setting.category.startswith(category)]
    
    def get_all_categories(self) -> List[str]:
        """Alle verfügbaren Kategorien auflisten"""
        categories = set()
        for setting in self.settings.values():
            categories.add(setting.category.split(" - ")[0])
        return sorted(list(categories))
    
    def format_registry_path(self, setting: RegistrySettingInfo, office_version: str = "16.0") -> str:
        """Registry-Pfad für spezifische Office-Version formatieren"""
        return setting.key_path.replace("{version}", office_version)
    
    def get_full_registry_info(self, setting_name: str, office_version: str = "16.0") -> Dict[str, Any]:
        """Vollständige Registry-Informationen für eine Einstellung"""
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
            "office_versions": setting.office_versions
        }
    
    def export_all_settings(self, office_version: str = "16.0") -> Dict[str, Any]:
        """Alle Einstellungen für Export/Dokumentation"""
        export_data = {
            "office_version": office_version,
            "settings_count": len(self.settings),
            "categories": self.get_all_categories(),
            "settings": {}
        }
        
        for name, setting in self.settings.items():
            if office_version in setting.office_versions:
                export_data["settings"][name] = self.get_full_registry_info(name, office_version)
        
        return export_data
    
    def validate_setting_value(self, setting_name: str, value: Any) -> bool:
        """Validiert ob ein Wert für eine Einstellung gültig ist"""
        setting = self.get_setting_by_name(setting_name)
        if not setting:
            return False
        
        if setting.value_type == "REG_DWORD":
            return isinstance(value, int) and 0 <= value <= 4294967295
        elif setting.value_type == "REG_SZ":
            return isinstance(value, str) and len(value) <= 260  # MAX_PATH
        
        return False