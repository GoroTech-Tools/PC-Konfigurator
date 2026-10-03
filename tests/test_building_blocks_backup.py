import logging
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import fs_retry
import pcconfig.office_template_manager as office_template_manager


class BuildingBlocksBackupTests(unittest.TestCase):
    def test_retries_transient_metadata_error_before_syncing_newer_user_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            user_path = root / "user" / "Building Blocks.dotx"
            backup_path = root / "templates" / "Sonstiges" / "Building Blocks" / "Building Blocks.dotx"
            user_path.parent.mkdir(parents=True)
            backup_path.parent.mkdir(parents=True)
            user_path.write_bytes(b"new user copy")
            backup_path.write_bytes(b"old backup copy")
            user_path.touch()
            backup_path.touch()
            user_path_mtime = 2_000_000_000
            backup_path_mtime = user_path_mtime - 1
            os.utime(user_path, (user_path_mtime, user_path_mtime))
            os.utime(backup_path, (backup_path_mtime, backup_path_mtime))

            manager = office_template_manager.OfficeTemplateManager.__new__(
                office_template_manager.OfficeTemplateManager,
            )
            manager.logger = logging.getLogger(__name__)
            manager.get_user_building_blocks_path = lambda: user_path

            original_stat = pathlib.Path.stat
            failed_once = False

            def flaky_stat(path, *args, **kwargs):
                nonlocal failed_once
                if path == backup_path and not failed_once:
                    failed_once = True
                    raise OSError(9, "Bad file descriptor")
                return original_stat(path, *args, **kwargs)

            def is_building_blocks_file(path):
                return path in {user_path, backup_path}

            with (
                patch.object(pathlib.Path, "is_file", new=is_building_blocks_file),
                patch.object(pathlib.Path, "stat", new=flaky_stat),
                patch.object(fs_retry.time, "sleep"),
            ):
                result = manager.sync_user_building_blocks_backup(root / "templates")

            self.assertTrue(failed_once)
            self.assertTrue(result["success"])
            self.assertEqual(result["status"], "backed_up")
            self.assertEqual(backup_path.read_bytes(), b"new user copy")


if __name__ == "__main__":
    unittest.main()
