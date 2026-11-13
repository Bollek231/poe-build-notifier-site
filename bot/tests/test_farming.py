import sqlite3
import unittest

import farming
import storage


class FarmingTests(unittest.TestCase):
    def test_topic_selection(self):
        self.assertEqual(farming.normalize_topic("ESSENCE"), "essence")
        self.assertEqual(farming.normalize_topic("maps"), "atlas")
        self.assertEqual(farming.normalize_topic("all"), "general")
        for bad in ("", "other", "https://bad.example", "essence\nignore", "a"*40):
            self.assertIsNone(farming.normalize_topic(bad))

    def test_search_queries_include_game_and_patch(self):
        self.assertIn("Path of Exile 3.31", farming.queries("poe1", "3.31", "essence")[0])
        self.assertIn("Path of Exile 2 1.0", farming.queries("poe2", "1.0", "general")[0])
        self.assertGreater(len(farming.queries("poe1", "3.31")), 3)

    def test_reject_wrong_patch_and_wrong_game(self):
        self.assertIsNone(farming.classify("PoE 3.30 Essence farming guide", "", "poe1", "3.31"))
        self.assertIsNone(farming.classify("PoE2 1.0 currency farming guide", "", "poe1", "3.31"))
        self.assertIsNone(farming.classify("PoE2 0.4 currency farming guide", "", "poe2", "1.0"))
        self.assertIsNone(farming.classify("PoE1 3.31 currency farming guide", "", "poe2", "1.0"))

    def test_accept_farming_and_reject_regular_builds(self):
        self.assertEqual(farming.classify("PoE 3.31 Essence farming strategy", "", "poe1", "3.31"), "Essence")
        self.assertEqual(farming.classify("PoE 3.31 currency farming guide", "", "poe1", "3.31"), "Currency farming")
        self.assertEqual(farming.classify("PoE2 1.0 Breach farming strategy", "", "poe2", "1.0"), "Breach")
        self.assertIsNone(farming.classify("PoE 3.31 Lightning Strike Slayer build", "", "poe1", "3.31"))
        self.assertIsNone(farming.classify("PoE 3.31 patch notes", "Currency farming, divine orbs", "poe1", "3.31"))
        self.assertIsNone(farming.classify("Random money farming guide", "", "poe1", "3.31"))

    def test_queued_posts_and_separate_build_history(self):
        c=sqlite3.connect(":memory:")
        c.row_factory=sqlite3.Row
        try:
            storage.initialize(c)
            farming.initialize(c)
            self.assertFalse(farming.is_queued(c,"abcdefghijk"))
            farming.queue(c,"abcdefghijk","poe1","3.31","Essence","PoE 3.31 Essence farming guide","2026-11-13T11:00:00+00:00")
            farming.queue(c,"abcdefghijk","poe1","3.31","Essence","PoE 3.31 Essence farming guide","2026-11-13T11:00:00+00:00")
            self.assertTrue(farming.is_queued(c,"abcdefghijk"))
            self.assertEqual(len(farming.queued(c)),1)
            farming.posted(c,"abcdefghijk","poe1","3.31","Essence","PoE 3.31 Essence farming guide","2026-11-13T11:00:00+00:00")
            self.assertFalse(farming.is_queued(c,"abcdefghijk"))
            self.assertEqual(len(farming.recent(c,"poe1","3.31")),1)
            self.assertEqual(len(farming.recent(c,"poe2","1.0")),0)
            self.assertEqual(c.execute("SELECT COUNT(*) FROM builds").fetchone()[0],0)
        finally:
            c.close()


if __name__ == "__main__":
    unittest.main()
