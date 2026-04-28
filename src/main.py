"""
PC-Konfigurator - Haupt-GUI-Anwendung
=====================================

Moderne GUI-Anwendung zur PC-Konfiguration mit CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import sys
import os
import subprocess

# --- sys.path-Anpassung für PyInstaller-Build (src als Datenordner) ---
if getattr(sys, 'frozen', False):
    # Im EXE-Modus: src-Ordner aus dem Bundle für dynamische Module
    sys.path.insert(0, os.path.join(getattr(sys, '_MEIPASS', ''), 'src'))
from pathlib import Path
from datetime import datetime

# Lokale Module importieren
from system_checker import SystemChecker
from office_configurator import OfficeConfigurator
from pcconfig.office_template_manager import OfficeTemplateManager
from safe_office_configurator import SafeOfficeConfigurator
from file_sync import FileSync
from font_installer import FontInstaller
from logger_config import setup_logging
from registry_gui import RegistryExplanationWindow
from build_info import BUILD_INFO

# Feste Auswahlliste der unterstützten Schriftarten.
# Schlüssel  = Anzeigename im Dropdown
# Wert       = Schriftname, den Windows/Office intern kennt
FONT_OPTIONS: dict[str, str] = {
    "Aptos":              "Aptos",
    "Aptos Narrow":       "Aptos Narrow",
    "Futura Cyrillic":    "Futura Cyrillic",
    "Glacial Indifference": "Glacial Indifference",
    "Montserrat":         "Montserrat",
    "PT Sans":            "PT Sans",
    "PT Sans Narrow":     "PT Sans Narrow",
    "Raleway":            "Raleway",
}


class PCKonfiguratorGUI:
    def _get_runtime_base_dir(self) -> Path:
        """Liefert das Basisverzeichnis der Anwendung."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent.parent

    def _get_icon_path(self) -> Path:
        """Ermittelt den Pfad zur ICO-Datei für GUI und EXE-Modus."""
        if getattr(sys, 'frozen', False):
            return Path(getattr(sys, '_MEIPASS', Path(sys.executable).resolve().parent)) / 'app_icon.ico'
        return Path(__file__).resolve().with_name('app_icon.ico')

    def _get_fonts_dir(self) -> Path:
        """Liefert das Fonts-Verzeichnis der Anwendung."""
        return self.app_dir / "Fonts"

    def _load_available_font_families(self):
        """Liefert die feste Auswahlliste der unterstützten Schriftarten."""
        return list(FONT_OPTIONS.keys())

    def _get_office_font_name(self) -> str:
        """Liefert den Windows-internen Schriftnamen für Office-Konfiguration."""
        return FONT_OPTIONS.get(self.font_name.get(), self.font_name.get())

    def _install_all_fonts(self):
        """Installiert alle Fonts aus dem Fonts-Ordner ins benutzerspezifische Fonts-Verzeichnis."""
        return self.font_installer.install_fonts_from_directory(self._get_fonts_dir())

    def add_tools_menu(self):
        # Menüleiste für CustomTkinter: immer direkt mit tk.Menu arbeiten
        tk_root = self.root._get_tk() if hasattr(self.root, '_get_tk') else self.root  # type: ignore[attr-defined]
        menubar = tk.Menu(tk_root)
        tk_root.config(menu=menubar)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Bitness- und COM-Check', command=self.run_bitness_check)
        tools_menu.add_command(label='GPO-Design-Prüfung', command=self.run_gpo_check)

    def run_gpo_check(self):
        """GPO-Prüfung auf Office-Design-Richtlinien als eigenständiges Dialogfenster."""
        from registry_explainer import RegistryExplainer
        import tkinter as tk
        import customtkinter as ctk

        result = RegistryExplainer().check_gpo_office_theme()

        win = ctk.CTkToplevel(self.root)
        win.title("GPO-Design-Prüfung")
        win.geometry("820x540")
        win.lift()
        win.focus_force()
        win.grab_set()

        # Status-Zeile
        if result["gpo_active"]:
            if result["theme_related_count"] > 0:
                status = (
                    f"⚠ GPO aktiv – {result['theme_related_count']} Theme-bezogene(r) Eintrag/Einträge "
                    f"gefunden (gesamt: {result['all_entries_count']})"
                )
                color = "#e07800"
            else:
                status = (
                    f"ℹ GPO aktiv – {result['all_entries_count']} Office-Richtlinie(n), "
                    "kein direkter Theme-Eintrag"
                )
                color = "#1f6aa5"
        else:
            status = "✓ Keine Office-Gruppenrichtlinien für Themes/Designs gefunden."
            color = "#2e8b57"

        ctk.CTkLabel(
            win, text=status,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color, wraplength=780, justify="left"
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            win, text=result["recommendation"],
            wraplength=780, justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 8))

        # Detailbox
        lines = ["Geprüfte Registry-Pfade:"]
        for p in result["checked_paths"]:
            lines.append(f"  {p}")
        if result["entries"]:
            lines.append("")
            lines.append("Gefundene Richtlinien-Einträge:")
            for e in result["entries"]:
                marker = " [⚠ THEME]" if e["theme_related"] else ""
                lines.append(f"  {e['path']}")
                lines.append(f"    {e['name']} = {e['data']!r}{marker}")
        else:
            lines.append("")
            lines.append("Keine Richtlinien-Einträge gefunden.")

        box = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=11))
        box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        box.insert("0.0", "\n".join(lines))
        box.configure(state="disabled")

        ctk.CTkButton(win, text="Schließen", command=win.destroy).pack(pady=(0, 12))

    def run_bitness_check(self):
        import sys
        import platform
        import logging
        import winreg
        from tkinter import messagebox
        import com_bitness_checker as checker

        log = logging.getLogger("bitness_check")
        log.info("Starte Bitness- und COM-Check...")

        def _decode_hresult(err: Exception):
            hresult = getattr(err, "hresult", None)
            if hresult is None and getattr(err, "args", None):
                first = err.args[0]
                if isinstance(first, int):
                    hresult = first

            if hresult is None:
                return None, None

            unsigned = hresult & 0xFFFFFFFF
            hex_code = f"0x{unsigned:08X}"

            mapping = {
                0x80040154: "Klasse nicht registriert (ProgID/COM-Registrierung fehlt)",
                0x80070005: "Zugriff verweigert (Berechtigungen/UAC)",
                0x80080005: (
                    "COM-Serverausführung fehlgeschlagen.\n"
                    "Ursache: Sehr wahrscheinlich Click-to-Run (C2R) Office.\n"
                    "C2R-Office nutzt eine virtualisierte COM-Registrierung, die von\n"
                    "64-Bit-Prozessen per win32com.client.Dispatch() nicht gestartet werden kann.\n"
                    "→ Die Kernfunktionen dieses Programms (Registry-basiert) sind davon NICHT betroffen."
                ),
                0x800401F3: "Ungültige Klassenzeichenfolge (ProgID falsch)",
                0x80029C4A: "Typbibliothek/DLL konnte nicht geladen werden",
            }
            return hex_code, mapping.get(unsigned, "Unbekannter COM-Fehler")

        def _get_com_registration(prog_id: str):
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\CLSID") as key:
                    clsid, _ = winreg.QueryValueEx(key, "")
                try:
                    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}\\LocalServer32") as key:
                        server, _ = winreg.QueryValueEx(key, "")
                    return clsid, server
                except OSError:
                    return clsid, None
            except OSError:
                return None, None

        try:
            lines = ["=== Office/Python Bitness-Checker ==="]

            # Python-Runtime (nur aktuelle Laufzeit, keine externen Prozesse)
            python_arch_raw = platform.architecture()[0]
            python_bitness = "64-bit" if "64" in python_arch_raw else "32-bit"
            lines.append(f"Python (aktuelle Laufzeit): {sys.executable} ({python_bitness})")

            # Office-Bitness prüfen
            office_bits = {}
            office_progids = {"Word": "Word.Application", "Excel": "Excel.Application"}
            for app in ["Word", "Excel"]:
                bit, path = checker.get_office_bitness(app)
                if bit:
                    lines.append(f"{app}: {bit} ({path})")
                    office_bits[app] = bit
                else:
                    lines.append(f"{app}: Bitness/Pfad nicht gefunden!")

            # COM-Registrierung schnell prüfen (ohne App-Start)
            lines.append("")
            lines.append("COM-Registrierung (schnell):")
            for app, prog_id in office_progids.items():
                clsid, server = _get_com_registration(prog_id)
                if clsid:
                    if server:
                        lines.append(f"- {app}: ProgID/CLSID OK ({clsid})")
                    else:
                        lines.append(f"- {app}: CLSID vorhanden ({clsid}), aber LocalServer32 fehlt")
                else:
                    lines.append(f"- {app}: ProgID nicht registriert ({prog_id})")

            # Bitness-Bewertung
            lines.append("")
            lines.append("Bewertung:")
            if office_bits:
                for app, office_bit in office_bits.items():
                    if office_bit != python_bitness:
                        lines.append(f"- {app}: Python {python_bitness} vs. Office {office_bit} -> normalerweise trotzdem COM-fähig (Out-of-Process).")
                    else:
                        lines.append(f"- {app}: Python und Office haben gleiche Bitness ({office_bit}).")
            else:
                lines.append("- Office-Bitness konnte nicht ermittelt werden.")

            if getattr(sys, 'frozen', False):
                lines.append("Hinweis: Check wurde im EXE-Modus ohne externe Python-Prozesse ausgeführt.")

            output = "\n".join(lines)
            log.info(output)
            messagebox.showinfo("Bitness- und COM-Check", output[-3000:])
        except Exception as e:
            log.error(f"Fehler beim Bitness-Check: {e}")
            messagebox.showerror("Fehler", str(e))
    
    def __init__(self):
        """Initialisierung der GUI"""
        self.version = BUILD_INFO.get("version", "?")
        self.setup_appearance()
        self.root = ctk.CTk()
        self.app_dir = self._get_runtime_base_dir()
        self.setup_main_window()
        
        # Komponenten initialisieren
        self.system_checker = SystemChecker()
        self.office_configurator = OfficeConfigurator()
        self.file_sync = FileSync()
        self.font_installer = FontInstaller()
        self.registry_gui = RegistryExplanationWindow(self.root, config_callback=self._get_registry_config)
        
        # Office Template Manager initialisieren
        self.template_manager = OfficeTemplateManager(self.app_dir)
        
        # Sicherer Office-Konfigurator initialisieren
        self.safe_office_config = SafeOfficeConfigurator(self.app_dir)
        
        # Logging setup
        self.logger = setup_logging()

        self.available_font_families = self._load_available_font_families()
        default_font_family = "Aptos" if "Aptos" in self.available_font_families else self.available_font_families[0]
        
        # Variablen für Konfiguration
        self.target_drive = tk.StringVar(value="Z:")
        self.use_documents = tk.BooleanVar(value=False)
        self.font_name = tk.StringVar(value=default_font_family)
        self.font_size_word = tk.IntVar(value=11)
        self.font_size_excel = tk.IntVar(value=10)
        
        self.create_widgets()
        self.add_tools_menu()
        # Systemstatus direkt beim Start im Hintergrund ermitteln
        self.root.after(500, self.check_system_requirements)
        
    def setup_appearance(self):
        """Erscheinungsbild der Anwendung festlegen"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
    def setup_main_window(self):
        """Hauptfenster konfigurieren"""
        self.root.title(f"PC-Konfigurator {self.version}")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Icon setzen (falls vorhanden)
        icon_path = self._get_icon_path()
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass
            
        # Hidden-Attribute für Ordner setzen
        self.set_hidden_directories()
            
    def set_hidden_directories(self):
        """Setzt Hidden-Attribute für _internal und logs Ordner"""
        if getattr(sys, 'frozen', False):
            # Ausführung als EXE
            exe_dir = Path(sys.executable).parent
            
            # _internal Ordner verstecken
            internal_dir = exe_dir / "_internal"
            if internal_dir.exists():
                try:
                    subprocess.run(["attrib", "+H", str(internal_dir)], check=False, capture_output=True)
                except Exception:
                    pass
            
            # logs Ordner verstecken (falls vorhanden)
            logs_dir = exe_dir / "logs"
            if logs_dir.exists():
                try:
                    subprocess.run(["attrib", "+H", str(logs_dir)], check=False, capture_output=True)
                except Exception:
                    pass
            
    def create_widgets(self):
        """GUI-Widgets erstellen"""
        # Hauptframe
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame, 
            text="PC-Konfigurator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Tabs erstellen
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs hinzufügen
        self.tabview.add("Übersicht")
        self.tabview.add("Konfiguration")
        self.tabview.add("Registry-Info")
        self.tabview.add("Ausführung")
        self.tabview.add("Logs")
        
        self.create_overview_tab()
        self.create_configuration_tab()
        self.create_registry_info_tab()
        self.create_execution_tab()
        self.create_logs_tab()
        
    def create_overview_tab(self):
        """Übersicht-Tab erstellen"""
        overview_frame = self.tabview.tab("Übersicht")
        
        # Überschrift: Willkommen
        welcome_title = ctk.CTkLabel(
            overview_frame,
            text="Willkommen beim PC-Konfigurator!",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_title.pack(anchor="w", padx=22, pady=(10, 0))

        # Fließtext
        welcome_text = ctk.CTkLabel(
            overview_frame,
            text="Diese Anwendung hilft Ihnen dabei, Ihren Windows-PC optimal für die Arbeit mit Office-Programmen zu konfigurieren.",
            wraplength=900,
            justify="left"
        )
        welcome_text.pack(anchor="w", padx=22, pady=(0, 8))

        # Abschnitt: Verfügbare Funktionen
        funktionen_label = ctk.CTkLabel(
            overview_frame,
            text="VERFÜGBARE FUNKTIONEN:",
            font=ctk.CTkFont(weight="bold")
        )
        funktionen_label.pack(anchor="w", padx=22, pady=(5, 0))
        funktionen_text = ctk.CTkLabel(
            overview_frame,
            text="• Datei-Vorlagen automatisch synchronisieren\n"
                 "• Office-Programme konfigurieren (Autokorrektur, Schriftarten, Pfade etc.)\n"
                 "• Windows-Explorer-Einstellungen optimieren\n"
                 "• Custom-Fonts installieren (Aptos, Montserrat, PT Sans etc.)",
            wraplength=900,
            justify="left"
        )
        funktionen_text.pack(anchor="w", padx=22, pady=(0, 8))

        # Abschnitt: So starten Sie
        starten_label = ctk.CTkLabel(
            overview_frame,
            text="SO STARTEN SIE:",
            font=ctk.CTkFont(weight="bold")
        )
        starten_label.pack(anchor="w", padx=22, pady=(5, 0))
        starten_text = ctk.CTkLabel(
            overview_frame,
            text="1. Tab 'Konfiguration' → Einstellungen nach Ihren Wünschen anpassen\n"
                 "2. Tab 'Registry-Info' → Geplante Änderungen einsehen (optional)\n"
                 "3. Tab 'Ausführung' → Konfiguration starten",
            wraplength=900,
            justify="left"
        )
        starten_text.pack(anchor="w", padx=22, pady=(0, 8))

        # Abschnitt: Vor der Ausführung
        vor_label = ctk.CTkLabel(
            overview_frame,
            text="VOR DER AUSFÜHRUNG:",
            font=ctk.CTkFont(weight="bold")
        )
        vor_label.pack(anchor="w", padx=22, pady=(5, 0))
        vor_text = ctk.CTkLabel(
            overview_frame,
            text="• Speichern Sie alle offenen Office-Dateien\n\nKlicken Sie auf den Reiter 'Konfiguration', um die Einstellungen anzupassen.",
            wraplength=900,
            justify="left"
        )
        vor_text.pack(anchor="w", padx=22, pady=(0, 8))
        
        # System-Status anzeigen
        status_frame = ctk.CTkFrame(overview_frame)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(status_frame, text="System-Status:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(status_frame, 
                                        text="Klicken Sie auf 'System prüfen' um Ihre Windows- und Office-Version zu ermitteln.",
                                        justify="left")
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        check_button = ctk.CTkButton(
            status_frame, 
            text="System prüfen", 
            command=self.check_system_requirements
        )
        check_button.pack(pady=10)
        
    def create_configuration_tab(self):
        """Konfiguration-Tab erstellen"""
        config_frame = self.tabview.tab("Konfiguration")
        
        # Haupt-Frame für kompakte Darstellung
        main_frame = ctk.CTkFrame(config_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Hinweistext für Konfiguration (kompakter)
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Konfigurationshinweise",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.pack(anchor="w", padx=10, pady=(8, 3))
        
        info_text = "Passen Sie die Einstellungen nach Ihren Bedürfnissen an. Alle Änderungen werden sicher in der Windows-Registry gespeichert."
        info_desc = ctk.CTkLabel(info_frame, text=info_text, wraplength=900)
        info_desc.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Zielverzeichnis-Sektion
        target_section = ctk.CTkFrame(main_frame)
        target_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(target_section, text="Zielverzeichnis für Datei-Vorlagen:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        
        target_hint = ctk.CTkLabel(
            target_section,
            text="Wählen Sie, wo die Office-Vorlagen gespeichert werden sollen:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        target_hint.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Radio-Buttons für Zielverzeichnis
        drive_radio = ctk.CTkRadioButton(
            target_section, 
            text="Laufwerk verwenden:", 
            variable=self.use_documents,
            value=False
        )
        drive_radio.pack(anchor="w", padx=20, pady=2)
        
        # Laufwerk-Eingabe
        drive_frame = ctk.CTkFrame(target_section)
        drive_frame.pack(fill="x", padx=30, pady=(5, 10))
        
        ctk.CTkLabel(drive_frame, text="Laufwerksbuchstabe:").pack(side="left", padx=5)
        
        # Dropdown für Laufwerksbuchstaben Z bis C (umgekehrte Reihenfolge)
        drive_options = [f"{chr(i)}:" for i in range(ord('Z'), ord('C') - 1, -1)]
        drive_menu = ctk.CTkOptionMenu(drive_frame, variable=self.target_drive, values=drive_options, width=80)
        drive_menu.pack(side="left", padx=5)
        
        drive_hint = ctk.CTkLabel(drive_frame, text="(Im BFW bitte das Laufwerk Z wählen.)", 
                     font=ctk.CTkFont(size=10), text_color="gray")
        drive_hint.pack(side="left", padx=10)
        
        docs_radio = ctk.CTkRadioButton(
            target_section,
            text="Dokumente-Verzeichnis verwenden",
            variable=self.use_documents,
            value=True
        )
        docs_radio.pack(anchor="w", padx=20, pady=(5, 15))
        
        # Schriftart-Sektion
        font_section = ctk.CTkFrame(main_frame)
        font_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(font_section, text="Schriftart-Konfiguration:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        font_hint = ctk.CTkLabel(
            font_section,
                text="Alle Schriften aus dem Ordner 'Fonts' werden automatisch im Benutzerprofil installiert. Die gewählte Schrift wird den Office-Vorlagen und der Registry zugewiesen:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        font_hint.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Schriftart-Auswahl
        font_frame = ctk.CTkFrame(font_section)
        font_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(font_frame, text="Schriftart:").pack(anchor="w", padx=5)
        
        font_menu = ctk.CTkOptionMenu(font_frame, variable=self.font_name, 
                                     values=self.available_font_families)
        font_menu.pack(anchor="w", padx=5, pady=5)
        
        # Schriftgrößen
        size_frame = ctk.CTkFrame(font_section)
        size_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Word/Outlook-Schriftgröße
        word_size_frame = ctk.CTkFrame(size_frame)
        word_size_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(word_size_frame, text="Word/Outlook-Schriftgröße:").pack(anchor="w", padx=5)
        word_size_menu = ctk.CTkOptionMenu(word_size_frame, variable=self.font_size_word,
                          values=["10", "11", "12"])
        word_size_menu.pack(anchor="w", padx=5, pady=5)
        
        # Excel-Schriftgröße
        excel_size_frame = ctk.CTkFrame(size_frame)
        excel_size_frame.pack(side="right", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(excel_size_frame, text="Excel-Schriftgröße:").pack(anchor="w", padx=5)
        excel_size_menu = ctk.CTkOptionMenu(excel_size_frame, variable=self.font_size_excel,
                           values=["10", "11", "12"])
        excel_size_menu.pack(anchor="w", padx=5, pady=5)
        
        # Office-Template-Sektion
        template_section = ctk.CTkFrame(main_frame)
        template_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(template_section, text="Office-Templates Verwaltung:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        template_hint = ctk.CTkLabel(
            template_section,
            text="Aktuelle Template-Status und Verwaltung für Normal.dotm (Word), Mappe.xltx (Excel) und E-Mail-Templates:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        template_hint.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Template-Status anzeigen
        self.template_status_frame = ctk.CTkFrame(template_section)
        self.template_status_frame.pack(fill="x", padx=20, pady=5)
        
        # Template-Buttons
        template_buttons_frame = ctk.CTkFrame(template_section)
        template_buttons_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        self.update_templates_button = ctk.CTkButton(
            template_buttons_frame,
            text="Templates sicher wiederherstellen",
            command=self.safe_restore_templates
        )
        self.update_templates_button.pack(side="left", padx=5, pady=5)
        
        self.check_templates_button = ctk.CTkButton(
            template_buttons_frame,
            text="Template-Status prüfen",
            command=self.check_safe_template_status
        )
        self.check_templates_button.pack(side="left", padx=5, pady=5)
        
        # Initiale Template-Status-Anzeige
        self.check_safe_template_status()
        
    def create_registry_info_tab(self):
        """Registry-Info Tab erstellen"""
        registry_frame = self.tabview.tab("Registry-Info")
        
        # Titel
        title_label = ctk.CTkLabel(
            registry_frame,
            text="Registry-Einstellungen Übersicht",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10)
        

        # Abschnitt: Was passiert
        was_passiert_label = ctk.CTkLabel(
            registry_frame,
            text="WAS PASSIERT:",
            font=ctk.CTkFont(weight="bold")
        )
        was_passiert_label.pack(anchor="w", padx=22, pady=(5, 0))
        was_passiert_text = ctk.CTkLabel(
            registry_frame,
            text="Diese Anwendung nimmt verschiedene Registry-Einstellungen für Office-Programme und Windows-System vor. Alle Änderungen werden detailliert dokumentiert und sind vollständig transparent.",
            wraplength=900,
            justify="left"
        )
        was_passiert_text.pack(anchor="w", padx=22, pady=(0, 8))

        # Abschnitt: Sicherheit
        sicherheit_label = ctk.CTkLabel(
            registry_frame,
            text="SICHERHEIT:",
            font=ctk.CTkFont(weight="bold")
        )
        sicherheit_label.pack(anchor="w", padx=22, pady=(5, 0))
        sicherheit_text = ctk.CTkLabel(
            registry_frame,
            text="• Alle Änderungen sind reversibel\n• Nur HKEY_CURRENT_USER wird modifiziert (sicher für Benutzer)\n• Keine Systemdateien werden verändert",
            wraplength=900,
            justify="left"
        )
        sicherheit_text.pack(anchor="w", padx=22, pady=(0, 8))

        # Abschnitt: Übersicht der Einstellungskategorien
        kategorie_label = ctk.CTkLabel(
            registry_frame,
            text="ÜBERSICHT DER EINSTELLUNGSKATEGORIEN:",
            font=ctk.CTkFont(weight="bold")
        )
        kategorie_label.pack(anchor="w", padx=22, pady=(5, 0))
        kategorie_text = ctk.CTkLabel(
            registry_frame,
            text=(
                "• Word - Benutzeroberfläche (Entwicklertools, Lineal)\n"
                "• Word - Formatierung (Formatierungszeichen, Tabellen)\n"
                "• Word - Datei-Vorlagen (DOT-PATH, STARTUP-PATH für Normal.dotm)\n"
                "• Word - Dateipfade und Schriftarten\n"
                "• Word - Autokorrektur-Einstellungen\n"
                "• Excel - Datei-Vorlagen (XLSTART-Info für Mappe.xltx)\n"
                "• Excel - Dateipfade und Schriftarten\n"
                "• Office - Allgemeine Einstellungen\n"
                "• Windows - Taskleiste und Kontextmenü"
            ),
            wraplength=900,
            justify="left"
        )
        kategorie_text.pack(anchor="w", padx=22, pady=(0, 8))

        # Hinweis
        hinweis_text = ctk.CTkLabel(
            registry_frame,
            text="Klicken Sie auf 'Detaillierte Ansicht öffnen' um alle geplanten Einstellungen mit ausführlichen Beschreibungen zu sehen.",
            wraplength=900,
            justify="left"
        )
        hinweis_text.pack(anchor="w", padx=22, pady=(0, 8))
        
        # Button darunter
        detail_button = ctk.CTkButton(
            registry_frame,
            text="Detaillierte Ansicht öffnen",
            command=self.open_registry_details,
            font=ctk.CTkFont(weight="bold")
        )
        detail_button.pack(pady=(10, 20))
        
    def create_execution_tab(self):
        """Ausführung-Tab erstellen"""
        execution_frame = self.tabview.tab("Ausführung")
        
        # Überschrift
        title_label = ctk.CTkLabel(
            execution_frame, 
            text="Konfiguration ausführen", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 5))

        # Anweisungstext optisch abgesetzt
        instruction_frame = ctk.CTkFrame(execution_frame)
        instruction_frame.pack(fill="x", padx=20, pady=(0, 10))

        instruction_text = """
    • System und Dateien: Fonts installieren, Templates synchronisieren, Office-Optimierung (Pfade)
    • Office konfigurieren: Schnelle Registry-Einstellungen für Office-Programme"""

        instruction_textbox = ctk.CTkTextbox(instruction_frame, height=60)
        instruction_textbox.pack(fill="x", padx=10, pady=8)
        instruction_textbox.insert("0.0", instruction_text)
        instruction_textbox.configure(state="disabled")

        # Buttons nebeneinander
        button_frame = ctk.CTkFrame(execution_frame)
        button_frame.pack(pady=(0, 10), padx=20, fill="x")

        execute_button = ctk.CTkButton(
            button_frame,
            text="Vollständige Konfiguration starten", 
            command=self.execute_all_configurations,
            width=220,
            height=40,
            font=ctk.CTkFont(weight="bold")
        )
        execute_button.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        partial_button = ctk.CTkButton(
            button_frame,
            text="Nur Office konfigurieren", 
            command=self.execute_office_only,
            width=180,
            height=40
        )
        partial_button.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        restart_explorer_button = ctk.CTkButton(
            execution_frame,
            text="Windows-Explorer neu starten",
            command=self.restart_windows_explorer,
            width=260,
            height=36
        )
        restart_explorer_button.pack(pady=(0, 10))

        # Status-Anzeige
        status_label = ctk.CTkLabel(execution_frame, text="Status und Fortschritt:",
                                   font=ctk.CTkFont(weight="bold"))
        status_label.pack(anchor="w", padx=20, pady=(10, 5))

        self.execution_status = ctk.CTkTextbox(
            execution_frame, 
            height=260,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.execution_status.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Initialer Text für Status-Anzeige
        initial_status = """🚀 PC-KONFIGURATOR - BEREIT ZUR AUSFÜHRUNG
==================================================

ℹ️ Anweisungen:
  • 'Vollständige Konfiguration starten' → Komplette Einrichtung
  • 'Nur Office konfigurieren' → Schnelle Registry-Optimierungen

📊 Der detaillierte Fortschritt wird hier live angezeigt.

🔴 Warten auf Benutzeraktion...
"""
        self.execution_status.insert("0.0", initial_status)
        # Legacy-Kompatibilität: ältere Methoden schreiben auf status_text
        self.status_text = self.execution_status
        
    def execute_all_configurations(self):
        """Alle Konfigurationen ausführen"""
        try:
            self.execution_status.delete("0.0", "end")
            self.execution_status.insert("0.0", "🚀 VOLLSTÄNDIGE KONFIGURATION GESTARTET\n" + "=" * 40 + "\n\n")
            
            # In separatem Thread ausführen
            thread = threading.Thread(target=self._run_full_configuration)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.execution_status.insert("end", f"FEHLER: {e}\n")
    
    def execute_office_only(self):
        """Nur Office-Konfiguration ausführen"""
        try:
            self.execution_status.delete("0.0", "end")
            self.execution_status.insert("0.0", "📝 OFFICE-KONFIGURATION GESTARTET\n" + "=" * 35 + "\n\n")
            
            # In separatem Thread ausführen
            thread = threading.Thread(target=self._run_office_configuration)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.execution_status.insert("end", f"FEHLER: {e}\n")
    
    def _run_full_configuration(self):
        """Vollständige Konfiguration in separatem Thread"""
        try:
            # System-Check
            self.execution_status.insert("end", "1. System-Check...\n")
            self.root.update()
            system_info = self.system_checker.get_system_info()
            self.execution_status.insert("end", f"   Erfolg: {system_info.get('platform', 'System')} erkannt\n")

            # Gewählte Font-Familie installieren
            self.execution_status.insert("end", "2. Alle Schriften aus dem Fonts-Ordner installieren...\n")
            self.root.update()
            font_result = self._install_all_fonts()
            if font_result.get('success'):
                installed_count = len(font_result.get('installed_fonts', []))
                self.execution_status.insert("end", f"   Erfolg: {installed_count} Schrift-Dateien im Benutzerprofil installiert\n")
            else:
                self.execution_status.insert("end", f"   Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n")
            
            # Office-Konfiguration
            self.execution_status.insert("end", "3. Office-Konfiguration...\n")
            self.root.update()
            
            office_settings = self._get_office_settings_from_gui()
            result = self.office_configurator.configure_all_settings(office_settings)
            
            if result['success']:
                applied_count = result.get('applied_count')
                if isinstance(applied_count, int):
                    self.execution_status.insert("end", f"   Erfolg: {applied_count} Einstellungen angewendet\n")
                else:
                    self.execution_status.insert("end", "   Erfolg: Office-Einstellungen angewendet\n")
                if result.get('word_start_screen_disabled'):
                    self.execution_status.insert("end", "   ✅ Word-Startbildschirm deaktiviert (Start mit leerem Dokument)\n")
                if result.get('outlook_warning'):
                    self.execution_status.insert("end", f"   ⚠️ Outlook-Vorlage: {result['outlook_warning']}\n")
            else:
                self.execution_status.insert("end", f"   Fehler: {result.get('error', 'Unbekannter Fehler')}\n")
            
            # Office-Templates wirklich anpassen + kopieren
            self.execution_status.insert("end", "4. Office-Templates anpassen und kopieren...\n")
            self.root.update()
            
            try:
                mod_results = self.template_manager.update_font_in_templates(
                    font_name=self._get_office_font_name(),
                    font_size_word=self.font_size_word.get(),
                    font_size_excel=self.font_size_excel.get()
                )
                copy_results = self.template_manager.copy_templates_to_user()
                safe_results = self.safe_office_config.configure_fonts_via_registry(
                    font_name=self._get_office_font_name(),
                    font_size_word=self.font_size_word.get(),
                    font_size_excel=self.font_size_excel.get()
                )
                
                mod_ok = bool(mod_results) and all(bool(v) for v in mod_results.values())
                copy_ok = bool(copy_results) and all(bool(v) for v in copy_results.values())
                registry_ok = all(bool(v) for k, v in safe_results.items() if k != 'error')

                if mod_ok and copy_ok:
                    self.execution_status.insert("end", "   ✅ Templates angepasst und ins Benutzerprofil kopiert\n")
                else:
                    self.execution_status.insert("end", "   ⚠️ Template-Anpassung/Kopie teilweise fehlgeschlagen (Details im Log)\n")

                if registry_ok:
                    self.execution_status.insert("end", f"   ✅ Schriftart konfiguriert: {self._get_office_font_name()}\n")
                    self.execution_status.insert("end", f"   ✅ Word: {self.font_size_word.get()}pt, Excel: {self.font_size_excel.get()}pt\n")
                else:
                    self.execution_status.insert("end", "   ⚠️ Registry-Schriftart-Konfiguration teilweise fehlgeschlagen\n")
                
            except Exception as template_error:
                self.execution_status.insert("end", f"   ❌ Template-Fehler: {template_error}\n")
            
            # Datei-Synchronisation (optional)
            # (Feature nicht aktiviert)
                
            self.execution_status.insert("end", "\nKonfiguration abgeschlossen!\n")
            self._add_registry_restart_notice()
            
        except Exception as e:
            self.execution_status.insert("end", f"\nFEHLER: {e}\n")
        
        self.root.update()
    
    def _run_office_configuration(self):
        """Nur Office-Konfiguration in separatem Thread"""
        try:
            self.execution_status.insert("end", "Office-Konfiguration startet...\n")
            font_result = self._install_all_fonts()
            if font_result.get('success'):
                installed_count = len(font_result.get('installed_fonts', []))
                self.execution_status.insert("end", f"Alle Schriften installiert: {installed_count} Dateien im Benutzerprofil\n")
            else:
                self.execution_status.insert("end", f"Warnung: Font-Installation fehlgeschlagen ({font_result.get('error', 'Unbekannter Fehler')})\n")
            self.root.update()
            
            office_settings = self._get_office_settings_from_gui()
            result = self.office_configurator.configure_all_settings(office_settings)
            
            if result['success']:
                applied_count = result.get('applied_count')
                if isinstance(applied_count, int):
                    self.execution_status.insert("end", f"Erfolg: {applied_count} Einstellungen angewendet\n")
                else:
                    self.execution_status.insert("end", "Erfolg: Office-Einstellungen angewendet\n")
                if result.get('word_start_screen_disabled'):
                    self.execution_status.insert("end", "✅ Word-Startbildschirm deaktiviert (Start mit leerem Dokument)\n")
                if result.get('outlook_warning'):
                    self.execution_status.insert("end", f"⚠️ Outlook-Vorlage: {result['outlook_warning']}\n")
                self.execution_status.insert("end", "Office-Konfiguration abgeschlossen!\n")
                self._add_registry_restart_notice()
            else:
                self.execution_status.insert("end", f"Fehler: {result.get('error', 'Unbekannter Fehler')}\n")
            
        except Exception as e:
            self.execution_status.insert("end", f"FEHLER: {e}\n")
        
        self.root.update()

    def _add_registry_restart_notice(self):
        """Hinweis für Anwender nach Registry-Anpassungen anzeigen."""
        notice = (
            "\nℹ️ Wichtiger Hinweis: Nach dem Anwenden der Registry-Einstellungen "
            "ist ein Neustart des Windows-Explorers oder eine Neuanmeldung am System empfohlen, "
            "damit alle Änderungen vollständig wirksam werden.\n"
        )
        self.execution_status.insert("end", notice)
        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "Hinweis zur Übernahme",
                "Die Registry-Einstellungen wurden angewendet.\n\n"
                "Bitte starten Sie den Windows-Explorer neu oder melden Sie sich einmal am System ab und wieder an, "
                "damit alle Änderungen vollständig wirksam werden."
            )
        )

    def restart_windows_explorer(self):
        """Startet den Windows-Explorer mit Rückfrage neu."""
        confirm = messagebox.askyesno(
            "Windows-Explorer neu starten",
            "Der Windows-Explorer wird jetzt neu gestartet.\n\n"
            "Dadurch werden Taskleiste und Desktop kurz neu geladen.\n"
            "Möchten Sie fortfahren?",
            icon="question"
        )

        if not confirm:
            return

        try:
            subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], check=False, capture_output=True)
            subprocess.Popen(["explorer.exe"])

            self.execution_status.insert(
                "end",
                "ℹ️ Windows-Explorer wurde neu gestartet. Änderungen sollten nun sichtbar sein.\n"
            )
            self.execution_status.see("end")
            messagebox.showinfo(
                "Explorer neu gestartet",
                "Der Windows-Explorer wurde neu gestartet.\n"
                "Die Registry-Änderungen sollten jetzt vollständig übernommen sein."
            )
        except Exception as e:
            self.execution_status.insert("end", f"⚠️ Explorer-Neustart fehlgeschlagen: {e}\n")
            self.execution_status.see("end")
            messagebox.showerror(
                "Fehler beim Explorer-Neustart",
                f"Der Explorer konnte nicht neu gestartet werden:\n{e}\n\n"
                "Bitte melden Sie sich am System ab und wieder an."
            )
    
    def _get_office_settings_from_gui(self):
        """Office-Einstellungen aus GUI-Eingaben extrahieren"""
        return {
              'font_name': self._get_office_font_name(),
            'font_size_word': self.font_size_word.get(),
            'font_size_excel': self.font_size_excel.get(),
            'target_drive': self.target_drive.get(),
            'use_documents_folder': self.use_documents.get()
        }

    def _get_registry_config(self) -> dict:
        """Gibt die aktuelle Konfiguration für die Registry-Info-Anzeige zurück."""
        try:
            if self.use_documents.get():
                path = str(Path.home() / "Documents")
            else:
                drive = self.target_drive.get()
                path = (drive + "\\") if drive and Path(drive + "\\").exists() else str(Path.home() / "Documents")
            return {
                'path': path,
                'font': self._get_office_font_name(),
                'font_size_word': self.font_size_word.get(),
                'font_size_excel': self.font_size_excel.get(),
            }
        except Exception:
            return {'path': str(Path.home() / "Documents"), 'font': 'Aptos', 'font_size_word': 11, 'font_size_excel': 10}
        
    def create_logs_tab(self):
        """Logs-Tab erstellen"""
        logs_frame = self.tabview.tab("Logs")
        
        # Log-Textbereich
        self.log_text = ctk.CTkTextbox(logs_frame, height=400)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button-Frame für Log-Aktionen
        log_button_frame = ctk.CTkFrame(logs_frame)
        log_button_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_button = ctk.CTkButton(
            log_button_frame,
            text="Logs aktualisieren",
            command=self.refresh_logs
        )
        refresh_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            log_button_frame,
            text="Logs löschen",
            command=self.clear_logs
        )
        clear_button.pack(side="left", padx=5)
        
        save_button = ctk.CTkButton(
            log_button_frame,
            text="Logs speichern",
            command=self.save_logs
        )
        save_button.pack(side="right", padx=5)
        
    def check_system_requirements(self):
        """System-Anforderungen in separatem Thread prüfen"""
        def check():
            try:
                result = self.system_checker.check_all_requirements()
                self.root.after(0, lambda: self.update_system_status(result))
            except Exception as e:
                self.logger.error(f"Fehler bei Systemprüfung: {e}")
                self.root.after(0, lambda: self.update_system_status({"success": False, "error": str(e)}))
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        
    def update_system_status(self, result):
        """System-Status in der GUI aktualisieren"""
        if result["success"]:
            office_bitness = result.get('office', {}).get('bitness', '?')
            status_text = (
                f"[OK] System OK\n"
                f"Windows: {result['windows_version']}\n"
                f"Office: {result['office_version']} ({office_bitness})"
            )
            self.status_label.configure(text=status_text, text_color="green", justify="left")
        else:
            self.status_label.configure(text=f"[FEHLER] {result.get('error', 'Unbekannter Fehler')}", 
                                      text_color="red", justify="left")
    
    def configure_office_settings(self, config):
        """Office-Einstellungen konfigurieren mit Hybrid Template-Manager"""
        try:
            # Schriftart und -größe aus Konfiguration extrahieren
            font_name = config.get('font_name', 'Aptos')
            font_size_word = config.get('font_size_word', 11)
            font_size_excel = config.get('font_size_excel', 10)
            self.add_status_text(f"🔧 Konfiguriere Office mit {font_name} (Word: {font_size_word}pt, Excel: {font_size_excel}pt)")

            # 1. Standards-Templates mit Schriftart anpassen
            self.add_status_text("📄 Standards-Templates werden angepasst...")
            mod_success = 0
            mod_total = 0
            copy_success = 0
            copy_total = 0
            modification_phase = {}
            copy_phase = {}
            overall_success = False

            # Schriftart in Templates anpassen
            try:
                mod_result = self.template_manager.update_font_in_templates(
                    font_name=font_name,
                    font_size_word=font_size_word,
                    font_size_excel=font_size_excel
                )
                modification_phase = {k: {'success': v} for k, v in mod_result.items()}
                mod_success = sum(1 for v in mod_result.values() if v)
                mod_total = len(mod_result)
            except Exception as e:
                self.logger.error(f"Fehler bei Template-Anpassung: {e}")
                self.add_status_text(f"❌ Fehler bei Template-Anpassung: {e}")

            # Templates ins Benutzerprofil kopieren
            self.add_status_text("📄 Standards-Templates werden kopiert...")
            try:
                copy_result = self.template_manager.copy_templates_to_user()
                copy_phase = {k: {'success': v} for k, v in copy_result.items()}
                copy_success = sum(1 for v in copy_result.values() if v)
                copy_total = len(copy_result)
            except Exception as e:
                self.logger.error(f"Fehler beim Kopieren der Templates: {e}")
                self.add_status_text(f"❌ Fehler beim Kopieren der Templates: {e}")

            # Status-Updates
            if mod_success == mod_total and mod_total > 0:
                self.add_status_text(f"✅ Alle {mod_total} Standards-Templates angepasst ({font_name})")
            elif mod_success > 0:
                self.add_status_text(f"⚠️ {mod_success}/{mod_total} Templates angepasst")
            else:
                self.add_status_text("❌ Template-Anpassung fehlgeschlagen")

            if copy_success == copy_total and copy_total > 0:
                self.add_status_text(f"✅ Alle {copy_total} Templates in Benutzerverzeichnisse kopiert")
            elif copy_success > 0:
                self.add_status_text(f"⚠️ {copy_success}/{copy_total} Templates kopiert")
            else:
                self.add_status_text("❌ Template-Kopierung fehlgeschlagen")

            overall_success = (mod_success == mod_total and copy_success == copy_total and mod_total > 0)
            template_results = {
                'modification_phase': modification_phase,
                'copy_phase': copy_phase,
                'overall_success': overall_success
            }

            # 2. Zusätzlich Registry-basierte Sicherheitskonfiguration
            registry_results = self.safe_office_config.configure_safe_office_defaults(
                font_name, font_size_word, font_size_excel
            )
            if registry_results['success']:
                self.add_status_text("✅ Registry-Konfiguration erfolgreich")
            else:
                self.add_status_text("⚠️ Registry-Konfiguration teilweise fehlgeschlagen")

            # 3. Alte Office-Konfiguration als Fallback
            fallback_results = self.office_configurator.configure_all_settings(config)

            # Gesamtergebnis bewerten
            overall_success = (
                template_results.get('overall_success', False) or 
                registry_results.get('success', False) or 
                fallback_results.get('success', False)
            )

            return {
                'success': overall_success,
                'template_results': template_results,
                'template_success': template_results.get('overall_success', False),
                'registry_results': registry_results,
                'fallback_results': fallback_results
            }

        except Exception as e:
            self.logger.error(f"Fehler bei Office-Konfiguration: {e}")
            self.add_status_text(f"❌ Fehler bei Office-Konfiguration: {e}")
            return {'success': False, 'error': str(e)}
        
    def add_status_text(self, text):
        """Text zur Status-Anzeige hinzufügen"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        target_widget = getattr(self, "status_text", None) or getattr(self, "execution_status", None)
        if target_widget is None:
            # Fallback für sehr frühe Initialisierungsphasen
            if hasattr(self, "logger"):
                self.logger.info(f"[{timestamp}] {text}")
            return
        target_widget.insert("end", f"[{timestamp}] {text}\n")
        target_widget.see("end")
        
    def refresh_logs(self):
        """Log-Dateien neu laden und anzeigen"""
        try:
            log_dir = self.app_dir / "logs"
            if not log_dir.exists():
                self.log_text.delete("0.0", "end")
                self.log_text.insert("0.0", "Keine Log-Dateien gefunden.")
                return
                
            # Neueste Log-Datei finden
            log_files = list(log_dir.glob("*.log"))
            if not log_files:
                self.log_text.delete("0.0", "end")
                self.log_text.insert("0.0", "Keine Log-Dateien gefunden.")
                return
                
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # Log-Inhalt lesen und anzeigen
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.log_text.delete("0.0", "end")
            self.log_text.insert("0.0", content)
            self.log_text.see("end")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Logs: {e}")
            
    def clear_logs(self):
        """Log-Anzeige leeren"""
        self.log_text.delete("0.0", "end")
        
    def save_logs(self):
        """Logs in Datei speichern"""
        try:
            content = self.log_text.get("0.0", "end")
            if not content.strip():
                messagebox.showwarning("Warnung", "Keine Logs zum Speichern vorhanden.")
                return
                
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log-Dateien", "*.log"), ("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Erfolg", f"Logs gespeichert in: {filename}")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Logs: {e}")
    
    def open_registry_details(self):
        """Detaillierte Registry-Ansicht mit Tabs und dynamischen Einstellungen öffnen"""
        self.registry_gui.show_window()
    
    def check_safe_template_status(self):
        """Überprüft den Status der Office-Templates mit sicherer Methode"""
        try:
            # Template-Status mit sicherer Methode ermitteln
            status = self.safe_office_config.check_template_status()
            
            # Bestehende Status-Widgets entfernen
            for widget in self.template_status_frame.winfo_children():
                widget.destroy()
            
            # Status-Anzeige erstellen
            status_info = "Template-Status (Sicherheitscheck):\\n\\n"
            
            template_names = {
                'normal_dotm': 'Word Standard-Template (Normal.dotm)',
                'mappe_xltx': 'Excel Standard-Template (Mappe.xltx)',
                'normal_email_dotm': 'Outlook E-Mail-Template (NormalEmail.dotm)'
            }
            
            for template_key, template_name in template_names.items():
                template_status = status[template_key]
                
                if template_status == "OK":
                    status_emoji = "✅"
                elif "Beschädigt" in template_status:
                    status_emoji = "⚠️"
                elif "Nicht vorhanden" in template_status:
                    status_emoji = "❌"
                else:
                    status_emoji = "⚠️"
                    
                status_info += f"{status_emoji} {template_name}\\n"
                status_info += f"   Status: {template_status}\\n\\n"
            
            status_label = ctk.CTkLabel(
                self.template_status_frame,
                text=status_info,
                justify="left",
                font=ctk.CTkFont(family="Courier New", size=11)
            )
            status_label.pack(anchor="w", padx=10, pady=5)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.template_status_frame,
                text=f"Fehler beim Überprüfen der Templates: {str(e)}",
                text_color="red"
            )
            error_label.pack(anchor="w", padx=10, pady=5)
    
    def safe_restore_templates(self):
        """Sichere Template-Wiederherstellung und Schriftart-Konfiguration"""
        try:
            # Warnung und Bestätigung
            result = messagebox.askyesno(
                "Sichere Template-Wiederherstellung",
                "SICHERE TEMPLATE-WIEDERHERSTELLUNG\\n\\n"
                "Was passiert:\\n"
                "✅ Beschädigte Templates werden durch Original-Versionen ersetzt\\n"
                "✅ Schriftart-Einstellungen werden über Registry gesetzt (sicher!)\\n"
                "✅ Keine direkte Template-Manipulation\\n\\n"
                f"Gewählte Schriftart: {self.font_name.get()}\\n"
                f"Word-Größe: {self.font_size_word.get()}pt\\n"
                f"Excel-Größe: {self.font_size_excel.get()}pt\\n\\n"
                "Fortfahren?",
                icon="question"
            )
            
            if not result:
                return
            
            # Progress-Dialog
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Sichere Template-Wiederherstellung...")
            progress_window.geometry("450x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ctk.CTkLabel(progress_window, text="Templates werden sicher wiederhergestellt...")
            progress_label.pack(pady=20)
            
            progress_details = ctk.CTkLabel(progress_window, text="", justify="left")
            progress_details.pack(pady=10)
            
            # Sichere Template-Konfiguration ausführen
            progress_details.configure(text="Sichere Schriftart-Konfiguration...")
            progress_window.update()

            font_install_result = self._install_all_fonts()
            
            results = self.safe_office_config.safe_font_setup(
                font_name=self._get_office_font_name(),
                font_size_word=self.font_size_word.get(),
                font_size_excel=self.font_size_excel.get()
            )
            
            progress_window.destroy()
            
            # Ergebnisse anzeigen
            if results['success']:
                recovered_templates = sum(results['template_recovery'].values())
                total_templates = len(results['template_recovery'])
                installed_font_count = len(font_install_result.get('installed_fonts', []))
                
                messagebox.showinfo(
                    "✅ Sichere Wiederherstellung erfolgreich!",
                    f"Templates und Schriftarten erfolgreich konfiguriert!\\n\\n"
                    f"📁 Templates wiederhergestellt: {recovered_templates}/{total_templates}\\n"
                    f"📝 Schriftart-Konfiguration: Erfolgreich\\n"
                    f"🔤 Installierte Font-Dateien: {installed_font_count}\\n\\n"
                    f"🎯 Neue Einstellungen:\\n"
                    f"• Schriftart: {self.font_name.get()}\\n"
                    f"• Word: {self.font_size_word.get()}pt\\n"
                    f"• Excel: {self.font_size_excel.get()}pt\\n\\n"
                    f"➤ Starten Sie Office-Programme neu für beste Ergebnisse!"
                )
            else:
                messagebox.showwarning(
                    "⚠️ Teilweise erfolgreich",
                    f"Wiederherstellung teilweise erfolgreich.\\n\\n"
                    f"Template-Wiederherstellung: {results['template_recovery']}\\n"
                    f"Font-Konfiguration: {results['font_configuration']}\\n\\n"
                    f"Überprüfen Sie die Log-Dateien für Details."
                )
            
            # Status neu laden
            self.check_safe_template_status()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei sicherer Template-Wiederherstellung: {str(e)}")
    
    def show_template_status(self):
        """Überprüft den Status der Office-Templates"""
        try:
            # Template-Status ermitteln
            status = self.template_manager.check_templates_exist()
            current_fonts = self.template_manager.get_current_fonts_in_templates()
            
            # Bestehende Status-Widgets entfernen
            for widget in self.template_status_frame.winfo_children():
                widget.destroy()
            
            # Status-Anzeige erstellen
            status_info = "Template-Status:\n\n"
            
            template_names = {
                'normal_dotm': 'Word Standard-Template (Normal.dotm)',
                'mappe_xltx': 'Excel Standard-Template (Mappe.xltx)',
                'normal_email_dotm': 'Outlook E-Mail-Template (NormalEmail.dotm)'
            }
            
            for template_key, template_name in template_names.items():
                exists = status[template_key]
                current_font = current_fonts[template_key]
                
                status_emoji = "✅" if exists else "❌"
                status_info += f"{status_emoji} {template_name}\n"
                status_info += f"   Aktuell: {current_font}\n\n"
            
            status_label = ctk.CTkLabel(
                self.template_status_frame,
                text=status_info,
                justify="left",
                font=ctk.CTkFont(family="Courier New", size=11)
            )
            status_label.pack(anchor="w", padx=10, pady=5)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.template_status_frame,
                text=f"Fehler beim Überprüfen der Templates: {str(e)}",
                text_color="red"
            )
            error_label.pack(anchor="w", padx=10, pady=5)
    
    def update_office_templates(self):
        """Kopiert und aktualisiert Office-Templates"""
        try:
            # Office-Prozess-Warnung anzeigen
            office_warning = messagebox.askyesno(
                "Office-Programme schließen",
                "WICHTIG: Für beste Ergebnisse sollten alle Office-Programme geschlossen sein.\n\n"
                "Sind Word, Excel und Outlook geschlossen?\n\n"
                "➤ JA: Fortfahren mit Template-Update\n"
                "➤ NEIN: Zuerst Office-Programme schließen",
                icon="question"
            )
            
            if not office_warning:
                messagebox.showinfo(
                    "Template-Update abgebrochen",
                    "Bitte schließen Sie alle Office-Programme und versuchen Sie es erneut.\n\n"
                    "Office-Programme:\n• Microsoft Word\n• Microsoft Excel\n• Microsoft Outlook\n• Microsoft PowerPoint"
                )
                return
            
            # Bestätigung vom Benutzer
            result = messagebox.askyesno(
                "Templates aktualisieren",
                "Möchten Sie die Office-Templates kopieren und mit der gewählten Schriftart aktualisieren?\n\n"
                f"Gewählte Schriftart: {self.font_name.get()}\n\n"
                "Was passiert:\n"
                "• Normal.dotm → Word Standard-Template\n"
                "• Mappe.xltx → Excel Standard-Template\n"
                "• NormalEmail.dotm → Outlook E-Mail-Template\n\n"
                "Bestehende Templates werden überschrieben!"
            )
            
            if not result:
                return
            
            # Progress-Dialog anzeigen (vereinfacht)
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("Templates werden aktualisiert...")
            progress_window.geometry("400x200")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ctk.CTkLabel(progress_window, text="Templates werden kopiert und aktualisiert...")
            progress_label.pack(pady=20)
            
            progress_details = ctk.CTkLabel(progress_window, text="", justify="left")
            progress_details.pack(pady=10)
            
            # Template-Operationen ausführen
            progress_details.configure(text="Schritt 1/2: Templates kopieren...")
            progress_window.update()
            
            progress_details.configure(text="Schritt 1/2: Schriftarten aktualisieren...")
            progress_window.update()

            # Schriftarten in Templates aktualisieren (zuerst!)
            font_results = self.template_manager.update_font_in_templates(
                font_name=self.font_name.get(),
                font_size_word=self.font_size_word.get(),
                font_size_excel=self.font_size_excel.get()
            )

            progress_details.configure(text="Schritt 2/2: Templates kopieren...")
            progress_window.update()

            # Templates erst nach Anpassung ins Benutzerprofil kopieren
            copy_results = self.template_manager.copy_templates_to_user()
            
            progress_window.destroy()
            
            # Ergebnisse anzeigen
            success_count = sum(copy_results.values()) + sum(font_results.values())
            total_operations = len(copy_results) + len(font_results)
            
            copy_success = sum(copy_results.values())
            font_success = sum(font_results.values())
            
            # Detaillierte Ergebnis-Analyse
            failed_templates = []
            successful_templates = []
            
            for template_key in copy_results.keys():
                copy_ok = copy_results[template_key]
                font_ok = font_results[template_key]
                
                template_names = {
                    'normal_dotm': 'Word Standard-Template',
                    'mappe_xltx': 'Excel Standard-Template', 
                    'normal_email_dotm': 'Outlook E-Mail-Template'
                }
                
                template_name = template_names.get(template_key, template_key)
                
                if copy_ok and font_ok:
                    successful_templates.append(f"✅ {template_name}")
                elif copy_ok and not font_ok:
                    failed_templates.append(f"⚠️ {template_name} (kopiert, aber Schriftart-Update fehlgeschlagen)")
                elif not copy_ok and font_ok:
                    failed_templates.append(f"⚠️ {template_name} (Schriftart aktualisiert, aber Kopieren fehlgeschlagen)")
                else:
                    failed_templates.append(f"❌ {template_name} (komplett fehlgeschlagen)")
            
            if success_count == total_operations:
                messagebox.showinfo(
                    "✅ Vollständig erfolgreich!",
                    f"Alle Templates erfolgreich aktualisiert!\n\n"
                    f"Erfolgreiche Templates:\n" +
                    "\n".join(successful_templates) +
                    f"\n\nNeue Standard-Schriftart: {self.font_name.get()}\n"
                    f"Word-Größe: {self.font_size_word.get()}pt, Excel-Größe: {self.font_size_excel.get()}pt\n\n"
                    f"➤ Neue Word-Dokumente verwenden jetzt {self.font_name.get()}!\n"
                    f"➤ Neue Excel-Dokumente verwenden jetzt {self.font_name.get()}!\n"
                    f"➤ Neue E-Mails verwenden jetzt {self.font_name.get()}!"
                )
            elif len(successful_templates) > 0:
                message = f"Templates teilweise aktualisiert:\n\n"
                
                if successful_templates:
                    message += "Erfolgreich:\n" + "\n".join(successful_templates) + "\n\n"
                
                if failed_templates:
                    message += "Probleme:\n" + "\n".join(failed_templates) + "\n\n"
                
                message += f"Mögliche Ursachen für Probleme:\n"
                message += f"• Office-Programme (Word/Excel/Outlook) sind noch geöffnet\n"
                message += f"• Template-Dateien werden von anderen Programmen verwendet\n\n"
                message += f"Empfehlung: Alle Office-Programme schließen und erneut versuchen."
                
                messagebox.showwarning("⚠️ Teilweise erfolgreich", message)
            else:
                messagebox.showerror(
                    "❌ Fehler bei Template-Update",
                    f"Leider konnten keine Templates aktualisiert werden.\n\n"
                    f"Mögliche Ursachen:\n"
                    f"• Office-Programme sind geöffnet (Word, Excel, Outlook)\n"
                    f"• Template-Dateien sind gesperrt\n"
                    f"• Keine Berechtigung für Template-Verzeichnisse\n\n"
                    f"Lösungsvorschläge:\n"
                    f"1. Alle Office-Programme schließen\n"
                    f"2. Als Administrator ausführen\n"
                    f"3. Überprüfen Sie die Log-Dateien für Details"
                )
            
            # Status neu laden
            self.check_safe_template_status()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Aktualisieren der Templates: {str(e)}")
    
    def run(self):
        """Anwendung starten"""
        self.root.mainloop()


def main():
    """Hauptfunktion"""
    try:
        app = PCKonfiguratorGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Kritischer Fehler", f"Anwendung konnte nicht gestartet werden: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()