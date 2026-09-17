"""Sicherung und Wiederherstellung von Microsoft-Edge-Profilen.

Die portable Sicherung liegt im vom Anwender gewählten Datei-Vorlagen-Ordner:

    Datei-Vorlagen/Sonstiges/Edge-Profile.zip
        ZIP-komprimiertes Archiv mit `User Data/` (Edge-Profilordner inkl. Local State)
    Datei-Vorlagen/Sonstiges/E-Mail-Signaturen/
        Outlook-Signaturen (falls vorhanden)

Cache- und Prozessdateien werden bewusst ausgelassen. Verschlüsselte Edge-
Anmeldedaten sind grundsätzlich an das Windows-Benutzerprofil gebunden und
können auf einem anderen Rechner ggf. nicht entschlüsselt werden.
"""

from __future__ import annotations

import filecmp
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from user_paths import get_documents_directory

from security_hints import describe_filesystem_error
from fs_retry import retry_on_oserror


class EdgeProfileManager:
    """Sichert und restauriert Edge-Profile und Outlook-Signaturen."""

    BACKUP_FOLDER_NAME = "Edge-Profile"
    SIGNATURE_BACKUP_FOLDER_NAME = "E-Mail-Signaturen"
    USER_DATA_FOLDER_NAME = "User Data"
    PROFILE_NAMES = {"Default"}

    # Temporäre, automatisch regenerierte oder häufig gesperrte Daten.
    IGNORED_NAMES = {
        "Cache",
        "Code Cache",
        "GPUCache",
        "DawnCache",
        "Crashpad",
        "BrowserMetrics",
        "GrShaderCache",
        "Service Worker",
        "SingletonCookie",
        "SingletonLock",
        "SingletonSocket",
    }

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)

    @property
    def edge_user_data_dir(self) -> Path:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return Path(local_app_data) / "Microsoft" / "Edge" / "User Data"

    @property
    def signatures_dir(self) -> Path:
        app_data = os.environ.get("APPDATA", "")
        return Path(app_data) / "Microsoft" / "Signatures"

    @classmethod
    def target_backup_dir(cls, office_settings: dict) -> Path:
        """Ermittelt den portablen Backup-Ordner aus den GUI-Einstellungen."""
        if office_settings.get("use_documents_folder"):
            base = get_documents_directory()
        else:
            drive = str(office_settings.get("target_drive", "")).strip()
            base = Path(drive + "\\") if drive else get_documents_directory()
        return base / "Datei-Vorlagen" / "Sonstiges" / cls.BACKUP_FOLDER_NAME

    @classmethod
    def target_signatures_dir(cls, office_settings: dict) -> Path:
        """Ermittelt den separaten portablen Ablageort für E-Mail-Signaturen."""
        return cls.target_backup_dir(office_settings).parent / cls.SIGNATURE_BACKUP_FOLDER_NAME

    @classmethod
    def target_backup_zip(cls, office_settings: dict) -> Path:
        """Ermittelt die ZIP-komprimierte, portable Edge-Profil-Sicherung."""
        return cls.target_backup_dir(office_settings).with_suffix(".zip")

    @classmethod
    def _legacy_backup_dir(cls, office_settings: dict) -> Path:
        """Ablageort vor Einführung des `Sonstiges`-Unterordners."""
        current = cls.target_backup_dir(office_settings)
        return current.parent.parent / cls.BACKUP_FOLDER_NAME

    @classmethod
    def _legacy_signatures_dir(cls, office_settings: dict) -> Path:
        return cls._legacy_backup_dir(office_settings).parent / cls.SIGNATURE_BACKUP_FOLDER_NAME

    @classmethod
    def _tree_matches(cls, reference: Path, candidate: Path) -> bool:
        """Prüft rekursiv (Größe/Änderungszeit), ob zwei Verzeichnisse übereinstimmen."""
        if not reference.is_dir() or not candidate.is_dir():
            return False
        comparison = filecmp.dircmp(reference, candidate, ignore=list(cls.IGNORED_NAMES))
        if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
            return False
        return all(cls._tree_matches(reference / name, candidate / name) for name in comparison.common_dirs)

    def cleanup_legacy_backup(self, office_settings: dict) -> dict:
        """Entfernt den alten Edge-/Signatur-Backup-Ordner (ohne `Sonstiges`),
        sofern er inhaltlich mit den aktuell vorhandenen Werten übereinstimmt."""
        removed: list[str] = []
        legacy_backup_dir = self._legacy_backup_dir(office_settings)
        new_backup_dir = self.target_backup_dir(office_settings)
        if legacy_backup_dir != new_backup_dir and self._has_backup(legacy_backup_dir):
            legacy_user_data = legacy_backup_dir / self.USER_DATA_FOLDER_NAME
            if self._tree_matches(self.edge_user_data_dir, legacy_user_data):
                shutil.rmtree(legacy_backup_dir, ignore_errors=True)
                removed.append(str(legacy_backup_dir))
                self.logger.info(
                    "Veraltetes Edge-Profil-Backup entfernt (identisch mit aktuellem Profil): %s",
                    legacy_backup_dir,
                )

        legacy_signatures_dir = self._legacy_signatures_dir(office_settings)
        new_signatures_dir = self.target_signatures_dir(office_settings)
        if (
            legacy_signatures_dir != new_signatures_dir
            and self._has_files(legacy_signatures_dir)
            and self._tree_matches(self.signatures_dir, legacy_signatures_dir)
        ):
            shutil.rmtree(legacy_signatures_dir, ignore_errors=True)
            removed.append(str(legacy_signatures_dir))
            self.logger.info(
                "Veraltetes Signatur-Backup entfernt (identisch mit aktuellen Signaturen): %s",
                legacy_signatures_dir,
            )

        return {"removed": removed}

    @classmethod
    def _is_profile_dir(cls, path: Path) -> bool:
        return path.is_dir() and (path.name in cls.PROFILE_NAMES or path.name.startswith("Profile "))

    @classmethod
    def _profile_dirs(cls, user_data_dir: Path) -> list[Path]:
        if not user_data_dir.is_dir():
            return []
        return sorted(
            (path for path in user_data_dir.iterdir() if cls._is_profile_dir(path)),
            key=lambda path: path.name.lower(),
        )

    @classmethod
    def _copy_ignore(cls, directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in cls.IGNORED_NAMES or name.startswith("Singleton")}

    @classmethod
    def _has_backup(cls, backup_dir: Path) -> bool:
        user_data = backup_dir / cls.USER_DATA_FOLDER_NAME
        return bool(cls._profile_dirs(user_data)) or (user_data / "Local State").is_file()

    @classmethod
    def _has_zip_backup(cls, zip_path: Path) -> bool:
        if not zip_path.is_file():
            return False
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                prefix = f"{cls.USER_DATA_FOLDER_NAME}/"
                return any(name.startswith(prefix) for name in zf.namelist())
        except zipfile.BadZipFile:
            return False

    @staticmethod
    def _has_files(directory: Path) -> bool:
        return directory.is_dir() and any(path.is_file() for path in directory.rglob("*"))

    def _close_edge(self) -> None:
        """Beendet Edge vor dem Zugriff auf gesperrte Profildateien."""
        try:
            subprocess.run(
                ["taskkill", "/IM", "msedge.exe", "/F"],
                check=False,
                capture_output=True,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )
            self.logger.info("Microsoft Edge wurde vor der Profil-Synchronisierung beendet.")
        except Exception as exc:
            self.logger.warning("Microsoft Edge konnte nicht beendet werden: %s", exc)

    @staticmethod
    def _copy_tree(source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=True,
            ignore=EdgeProfileManager._copy_ignore,
        )

    @staticmethod
    def _zip_directory(source_dir: Path, zip_path: Path) -> None:
        """Packt ein Verzeichnis rekursiv in ein ZIP-Archiv (Datei für Datei, tolerant
        gegen einzelne nicht lesbare/gesperrte Dateien)."""
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                try:
                    zf.write(file_path, file_path.relative_to(source_dir))
                except OSError:
                    continue

    def restore(self, office_settings: dict) -> dict:
        """Stellt ein vorhandenes Backup im aktuellen Windows-Benutzerprofil wieder her."""
        backup_zip = self.target_backup_zip(office_settings)
        backup_signatures = self.target_signatures_dir(office_settings)
        has_edge_backup = self._has_zip_backup(backup_zip)
        has_signature_backup = self._has_files(backup_signatures)
        if not has_edge_backup and not has_signature_backup:
            return {
                "success": True,
                "restored": False,
                "profiles": 0,
                "signatures": False,
                "signature_backup_available": False,
                "message": "Kein Edge- oder Signatur-Backup vorhanden.",
            }

        if has_edge_backup:
            self._close_edge()
        restored_profiles = 0
        restored_signatures = False
        extract_dir: Path | None = None
        try:
            if has_edge_backup:
                extract_dir = Path(tempfile.mkdtemp(prefix="pckconfig-edge-restore-"))
                with zipfile.ZipFile(backup_zip, "r") as zf:
                    zf.extractall(extract_dir)
                backup_user_data = extract_dir / self.USER_DATA_FOLDER_NAME
                self.edge_user_data_dir.mkdir(parents=True, exist_ok=True)
                for source in self._profile_dirs(backup_user_data):
                    self._copy_tree(source, self.edge_user_data_dir / source.name)
                    restored_profiles += 1

                local_state = backup_user_data / "Local State"
                if local_state.is_file():
                    shutil.copy2(local_state, self.edge_user_data_dir / local_state.name)

            if not self._has_files(self.signatures_dir) and self._has_files(backup_signatures):
                self._copy_tree(backup_signatures, self.signatures_dir)
                restored_signatures = True
                self.logger.info("E-Mail-Signaturen wurden in das leere Benutzerverzeichnis wiederhergestellt.")

            parts = []
            if has_edge_backup:
                parts.append(f"{restored_profiles} Edge-Profil(e)")
            if restored_signatures:
                parts.append("E-Mail-Signaturen")
            message = " und ".join(parts) + " wiederhergestellt." if parts else (
                "Vorhandene E-Mail-Signaturen wurden beibehalten."
            )
            self.logger.info(message)
            return {
                "success": True,
                "restored": bool(restored_profiles or restored_signatures),
                "profiles": restored_profiles,
                "signatures": restored_signatures,
                "signature_backup_available": has_signature_backup,
                "message": message,
            }
        except Exception as exc:
            self.logger.error("Edge-Backup konnte nicht wiederhergestellt werden: %s", exc, exc_info=True)
            error_text = describe_filesystem_error(exc) if isinstance(exc, OSError) else str(exc)
            return {"success": False, "restored": False, "error": error_text}
        finally:
            if extract_dir is not None:
                shutil.rmtree(extract_dir, ignore_errors=True)

    def backup(self, office_settings: dict) -> dict:
        """Sichert vorhandene Edge-Profile und Signaturen in den Zielordner."""
        try:
            self.cleanup_legacy_backup(office_settings)
        except Exception as exc:
            self.logger.warning("Veraltetes Backup konnte nicht bereinigt werden: %s", exc)
        profiles = self._profile_dirs(self.edge_user_data_dir)
        signatures_exist = self._has_files(self.signatures_dir)
        if not profiles and not signatures_exist:
            return {
                "success": True,
                "backed_up": False,
                "profiles": 0,
                "signatures": False,
                "message": "Keine Edge-Profile oder E-Mail-Signaturen gefunden.",
            }

        if profiles:
            self._close_edge()
        backup_zip = self.target_backup_zip(office_settings)
        legacy_raw_dir = self.target_backup_dir(office_settings)
        temporary_zip: Path | None = None
        staging_dir: Path | None = None
        try:
            if profiles:
                staging_dir = Path(tempfile.mkdtemp(prefix="pckconfig-edge-backup-"))
                user_data_target = staging_dir / self.USER_DATA_FOLDER_NAME
                user_data_target.mkdir(parents=True, exist_ok=True)
                for source in profiles:
                    self._copy_tree(source, user_data_target / source.name)

                local_state = self.edge_user_data_dir / "Local State"
                if local_state.is_file():
                    shutil.copy2(local_state, user_data_target / local_state.name)

                # Das Archiv lokal erzeugen. OneDrive kann Zielordner während einer
                # laufenden Synchronisierung kurzzeitig ausblenden; ein lokales
                # Zwischenarchiv verhindert dadurch Abbrüche beim Öffnen der ZIP.
                temporary_zip = staging_dir.parent / (staging_dir.name + ".zip")
                if temporary_zip.exists():
                    temporary_zip.unlink()
                self._zip_directory(staging_dir, temporary_zip)
                retry_on_oserror(lambda: backup_zip.parent.mkdir(parents=True, exist_ok=True))
                retry_on_oserror(lambda: shutil.copy2(temporary_zip, backup_zip))

                # Die frühere, unkomprimierte Sicherung wird ab sofort durch das ZIP
                # ersetzt und ist damit überflüssig.
                if legacy_raw_dir.is_dir():
                    shutil.rmtree(legacy_raw_dir, ignore_errors=True)
                    self.logger.info(
                        "Unkomprimiertes Edge-Profil-Backup entfernt (ersetzt durch ZIP): %s",
                        legacy_raw_dir,
                    )

            if signatures_exist:
                signature_target = self.target_signatures_dir(office_settings)
                signature_temp = signature_target.with_name(signature_target.name + ".pckconfig-tmp")
                if signature_temp.exists():
                    shutil.rmtree(signature_temp, ignore_errors=True)
                retry_on_oserror(lambda: signature_target.parent.mkdir(parents=True, exist_ok=True))
                self._copy_tree(self.signatures_dir, signature_temp)
                if signature_target.exists():
                    shutil.rmtree(signature_target, ignore_errors=True)
                retry_on_oserror(lambda: os.replace(signature_temp, signature_target))

            parts = []
            if profiles:
                parts.append(f"{len(profiles)} Edge-Profil(e)")
            if signatures_exist:
                parts.append("E-Mail-Signaturen")
            message = " und ".join(parts) + " gesichert."
            self.logger.info("%s Ziel: %s", message, backup_zip)
            return {
                "success": True,
                "backed_up": True,
                "profiles": len(profiles),
                "signatures": signatures_exist,
                "message": message,
            }
        except Exception as exc:
            self.logger.error("Edge-Profile konnten nicht gesichert werden: %s", exc, exc_info=True)
            error_text = describe_filesystem_error(exc) if isinstance(exc, OSError) else str(exc)
            return {"success": False, "backed_up": False, "error": error_text}
        finally:
            if temporary_zip is not None:
                temporary_zip.unlink(missing_ok=True)
            if staging_dir is not None:
                shutil.rmtree(staging_dir, ignore_errors=True)
