"""Offline regression checks for the Windows updater."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import launcher_updater as update


class VersionTests(unittest.TestCase):
    def test_release_order(self):
        self.assertTrue(update.is_newer("0.6.3", "0.6.2b"))
        self.assertFalse(update.is_newer("0.6.2b", "0.6.3"))
        self.assertTrue(update.is_newer("0.6.2b", "0.6.2a"))
        self.assertFalse(update.is_newer("0.6.3", "0.6.3"))
        self.assertTrue(update.is_newer("0.7.0", "0.6.9"))

    def test_bad_version_rejected(self):
        for bad in ("abc", "v0.6.3", "0.6.3/../", "0.6.x", ""):
            with self.subTest(version=bad):
                with self.assertRaises(ValueError):
                    update.version_key(bad)

    def test_does_not_download_when_current(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "VERSION").write_text("0.6.3", encoding="utf-8")
            with patch.object(update, "request", side_effect=AssertionError("unexpected fetch")):
                self.assertFalse(update.install(root, "a" * 40, "0.6.3"))

    def test_private_files_are_not_update_targets(self):
        for forbidden in (".env", "search_config.json", "poe330_seen.sqlite3", "backups"):
            self.assertNotIn(forbidden, update.FILES)


if __name__ == "__main__":
    unittest.main()
