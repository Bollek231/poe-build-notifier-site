"""Regression checks for Windows WinError 32 in SQLite online backup (v0.6.5a)."""
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import backups


NOW = datetime(2026, 11, 16, 13, 0, tzinfo=timezone.utc)


class ClosingConnection(sqlite3.Connection):
    """Spy on explicit close, not just sqlite3 commit-context exit."""
    active = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.closed_explicitly = False
        self.active.append(self)

    def close(self):
        self.closed_explicitly = True
        return super().close()


class WindowsBackupRegressionTests(unittest.TestCase):
    def make_source(self, directory):
        src = directory / "poe330_seen.sqlite3"
        with sqlite3.connect(src) as c:
            c.execute("CREATE TABLE example(data TEXT NOT NULL)")
            c.execute("INSERT INTO example VALUES ('keep me')")
        return src

    def test_file_handles_closed_before_rename(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            src = self.make_source(folder)
            original_connect = sqlite3.connect
            original_replace = backups.os.replace
            ClosingConnection.active.clear()

            def tracked_connect(*args, **kwargs):
                kwargs["factory"] = ClosingConnection
                return original_connect(*args, **kwargs)

            def checked_replace(source, destination):
                self.assertGreaterEqual(len(ClosingConnection.active), 2)
                self.assertTrue(all(c.closed_explicitly for c in ClosingConnection.active))
                return original_replace(source, destination)

            with patch.object(backups.sqlite3, "connect", side_effect=tracked_connect), \
                 patch.object(backups.os, "replace", side_effect=checked_replace):
                dest, created = backups.backup_database(src, folder / "backups", now=NOW)

            self.assertTrue(created)
            self.assertTrue(dest.exists())
            with original_connect(dest) as verify:
                self.assertEqual(verify.execute("SELECT data FROM example").fetchone(),
                                 ("keep me",))
            self.assertFalse(list((folder / "backups").glob("*.tmp")))
            self.assertTrue(src.exists())

    def test_temporary_windows_lock_retried_without_corrupting_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            src = self.make_source(folder)
            original_replace = backups.os.replace
            calls = []

            def momentary_windows_lock(source, destination):
                calls.append((source, destination))
                if len(calls) == 1:
                    exc = PermissionError("locked by indexer")
                    exc.winerror = 32
                    raise exc
                return original_replace(source, destination)

            with patch.object(backups.os, "replace", side_effect=momentary_windows_lock), \
                 patch.object(backups.time, "sleep", return_value=None) as sleep:
                dest, created = backups.backup_database(src, folder / "backups", now=NOW)
            self.assertTrue(created)
            self.assertTrue(dest.exists())
            self.assertEqual(len(calls), 2)
            sleep.assert_called_once_with(0.15)
            self.assertTrue(src.exists())

    def test_real_permission_error_does_not_retry_or_remove_original(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            src = self.make_source(folder)
            with patch.object(backups.os, "replace",
                              side_effect=PermissionError("permanently denied")) as replace, \
                 patch.object(backups.time, "sleep") as sleep:
                with self.assertRaises(PermissionError):
                    backups.backup_database(src, folder / "backups", now=NOW)
            replace.assert_called_once()
            sleep.assert_not_called()
            self.assertTrue(src.exists())
            self.assertFalse(list((folder / "backups").glob("*.tmp")))

    def test_backup_created_once_per_day_and_live_data_survives(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            src = self.make_source(folder)
            first, created = backups.backup_database(src, folder / "backups", now=NOW)
            second, created_again = backups.backup_database(src, folder / "backups", now=NOW)
            self.assertEqual(first, second)
            self.assertTrue(created)
            self.assertFalse(created_again)
            self.assertEqual(len(list((folder / "backups").glob("*.sqlite3"))), 1)
            self.assertTrue(src.exists())


if __name__ == "__main__":
    unittest.main()
