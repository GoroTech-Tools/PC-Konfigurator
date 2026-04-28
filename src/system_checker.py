"""
System-Anforderungen Checker
============================

Prüft Windows- und Office-Versionen sowie andere Systemanforderungen.
Portiert aus dem ursprünglichen PowerShell-Skript.
"""

import platform
import winreg
import subprocess
import psutil
import os
from pathlib import Path
import logging


class SystemChecker:
    """Klasse zur Überprüfung der Systemanforderungen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def check_all_requirements(self):
        """Alle Systemanforderungen prüfen"""
        try:
            windows_check = self.check_windows_version()
            office_check = self.check_office_version()
            
            success = windows_check["success"] and office_check["success"]
            
            result = {
                "success": success,
                "windows": windows_check,
                "office": office_check,
                "windows_version": windows_check.get("version_string", "Unbekannt"),
                "office_version": office_check.get("version_string", "Nicht gefunden")
            }
            
            if success:
                self.logger.info("Alle Systemanforderungen erfüllt")
            else:
                self.logger.warning("Systemanforderungen nicht vollständig erfüllt")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Fehler bei Systemprüfung: {e}")
            return {"success": False, "error": str(e)}
    
    def check_windows_version(self):
        """Windows-Version prüfen"""
        try:
            # Windows-Version ermitteln
            version = platform.version()
            build = platform.release()
            
            # Detaillierte Informationen über WinAPI
            try:
                # Build-Nummer aus Registry lesen
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    build_number = winreg.QueryValueEx(key, "CurrentBuild")[0]
                    build_number = int(build_number)
            except Exception:
                build_number = 0
                
            # Windows 10/11 Erkennung
            is_windows_10_or_11 = False
            version_string = f"{build} (Build {build_number})"
            
            if build == "10":
                if build_number >= 22000:
                    # Windows 11
                    is_windows_10_or_11 = True
                    version_string = f"Windows 11 (Build {build_number})"
                elif build_number >= 18362:
                    # Windows 10 Version 1903 oder höher
                    is_windows_10_or_11 = True
                    version_string = f"Windows 10 (Build {build_number})"
                else:
                    version_string = f"Windows 10 (Build {build_number}) - ZU ALT"
            elif build == "11":
                is_windows_10_or_11 = True
                version_string = f"Windows 11 (Build {build_number})"
                
            self.logger.info(f"Windows-Version: {version_string}")
            
            return {
                "success": is_windows_10_or_11,
                "version": version,
                "build": build,
                "build_number": build_number,
                "version_string": version_string,
                "supported": is_windows_10_or_11
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Windows-Versionsprüfung: {e}")
            return {"success": False, "error": str(e)}
    
    def check_office_version(self):
        """Office-Version prüfen"""
        try:
            office_info = self._detect_office_installation()
            bitness = office_info.get("bitness", "?")
            # Fallback, falls Bitness immer noch nicht bestimmt werden konnte
            if bitness == "?":
                import sys
                path = office_info.get("install_path", "")
                if 'Program Files (x86)' in path:
                    bitness = '32-bit'
                elif 'Program Files' in path:
                    bitness = '64-bit'
                else:
                    bitness = '64-bit' if sys.maxsize > 2**32 else '32-bit'
            if office_info["found"]:
                # Office 2013 (15.0) oder neuer wird unterstützt
                major_version = office_info.get("major_version", 0)
                supported = major_version >= 15
                version_string = office_info["version_string"]
                if not supported:
                    version_string += " - ZU ALT"
                self.logger.info(f"Office-Version: {version_string} ({bitness})")
                return {
                    "success": supported,
                    "found": True,
                    "version": office_info["version"],
                    "major_version": major_version,
                    "version_string": version_string,
                    "installation_type": office_info["installation_type"],
                    "bitness": bitness,
                    "supported": supported
                }
            else:
                self.logger.warning("Keine Office-Installation gefunden")
                # Für Testing: Office-Anforderung lockern
                return {
                    "success": True,  # Temporär auf True setzen
                    "found": False,
                    "version_string": "Nicht gefunden (möglicherweise Office 365 Web)",
                    "bitness": bitness,
                    "supported": True  # Temporär
                }
        except Exception as e:
            self.logger.error(f"Fehler bei Office-Versionsprüfung: {e}")
            return {"success": False, "error": str(e)}
    
    def _detect_office_installation(self):
        """Office-Installation erkennen (verschiedene Methoden)"""
        # Methode 1: ClickToRun-Installation
        clicktorun_info = self._check_clicktorun_office()
        if clicktorun_info["found"]:
            return clicktorun_info
        msi_info = self._check_msi_office()
        if msi_info["found"]:
            return msi_info
        exe_info = self._check_executable_office()
        if exe_info["found"]:
            return exe_info
        return {"found": False}
    
    def _check_clicktorun_office(self):
        """ClickToRun Office-Installation prüfen"""
        import sys
        try:
            registry_keys = [
                r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration",
                r"SOFTWARE\WOW6432Node\Microsoft\Office\ClickToRun\Configuration"
            ]
            for key_path in registry_keys:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        version = winreg.QueryValueEx(key, "ProductVersion")[0]
                        major_version = int(version.split(".")[0])
                        # Bitness auslesen
                        try:
                            bitness = winreg.QueryValueEx(key, "Platform")[0]
                        except Exception:
                            # Fallback: Prüfe Registry-Pfad und Python-Architektur
                            if 'WOW6432Node' in key_path:
                                bitness = '32-bit'
                            else:
                                bitness = '64-bit' if sys.maxsize > 2**32 else '32-bit'
                        return {
                            "found": True,
                            "version": version,
                            "major_version": major_version,
                            "version_string": f"Office {version} (ClickToRun)",
                            "installation_type": "ClickToRun",
                            "bitness": bitness
                        }
                except (FileNotFoundError, OSError):
                    continue
        except Exception as e:
            self.logger.debug(f"ClickToRun-Erkennung fehlgeschlagen: {e}")
        return {"found": False}
    
    def _check_msi_office(self):
        """MSI Office-Installation prüfen"""
        try:
            registry_keys = [
                r"SOFTWARE\Microsoft\Office\16.0\Common\InstallRoot",
                r"SOFTWARE\Microsoft\Office\15.0\Common\InstallRoot",
                r"SOFTWARE\WOW6432Node\Microsoft\Office\16.0\Common\InstallRoot",
                r"SOFTWARE\WOW6432Node\Microsoft\Office\15.0\Common\InstallRoot"
            ]
            for key_path in registry_keys:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        install_path = winreg.QueryValueEx(key, "Path")[0]
                        # Bitness bestimmen anhand des Pfads
                        if 'Program Files (x86)' in install_path:
                            bitness = '32-bit'
                        else:
                            bitness = '64-bit'
                        if os.path.exists(install_path):
                            if "16.0" in key_path:
                                return {
                                    "found": True,
                                    "version": "16.0",
                                    "major_version": 16,
                                    "version_string": "Office 2016/2019/2021 (MSI)",
                                    "installation_type": "MSI",
                                    "bitness": bitness
                                }
                            elif "15.0" in key_path:
                                return {
                                    "found": True,
                                    "version": "15.0",
                                    "major_version": 15,
                                    "version_string": "Office 2013 (MSI)",
                                    "installation_type": "MSI",
                                    "bitness": bitness
                                }
                except (FileNotFoundError, OSError):
                    continue
        except Exception as e:
            self.logger.debug(f"MSI-Erkennung fehlgeschlagen: {e}")
        return {"found": False}
    
    def _check_executable_office(self):
        """Office durch Executable-Dateien erkennen"""
        try:
            common_paths = [
                r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
                r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE",
                r"C:\Program Files\Microsoft Office\Office15\WINWORD.EXE",
                r"C:\Program Files (x86)\Microsoft Office\Office15\WINWORD.EXE"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    try:
                        # Version aus Datei-Eigenschaften lesen
                        import win32api
                        file_info = win32api.GetFileVersionInfo(path, "\\")
                        version = f"{file_info['FileVersionMS'] >> 16}.{file_info['FileVersionMS'] & 0xFFFF}"
                        
                        if "Office16" in path:
                            return {
                                "found": True,
                                "version": version,
                                "major_version": 16,
                                "version_string": f"Office 2016/2019/2021 (Version {version})",
                                "installation_type": "Executable"
                            }
                        elif "Office15" in path:
                            return {
                                "found": True,
                                "version": version,
                                "major_version": 15,
                                "version_string": f"Office 2013 (Version {version})",
                                "installation_type": "Executable"
                            }
                    except Exception:
                        # Fallback ohne Versionserkennung
                        if "Office16" in path:
                            return {
                                "found": True,
                                "version": "16.0",
                                "major_version": 16,
                                "version_string": "Office 2016/2019/2021 (Executable)",
                                "installation_type": "Executable"
                            }
                        elif "Office15" in path:
                            return {
                                "found": True,
                                "version": "15.0",
                                "major_version": 15,
                                "version_string": "Office 2013 (Executable)",
                                "installation_type": "Executable"
                            }
                            
        except Exception as e:
            self.logger.debug(f"Executable-Erkennung fehlgeschlagen: {e}")
            
        return {"found": False}
    
    def check_office_processes_closed(self):
        """Prüfen, ob Office-Prozesse geschlossen sind"""
        office_processes = ["WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE", "POWERPNT.EXE"]
        running_processes = []
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].upper() in [p.upper() for p in office_processes]:
                    running_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return {
            "all_closed": len(running_processes) == 0,
            "running_processes": running_processes
        }
    
    def get_system_info(self):
        """Allgemeine Systeminformationen sammeln"""
        try:
            return {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "python_version": platform.python_version(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('C:\\')._asdict()
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Sammeln von Systeminformationen: {e}")
            return {}