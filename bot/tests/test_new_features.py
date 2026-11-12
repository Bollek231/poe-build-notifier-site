import sqlite3
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import features
import storage

class LeagueAndDigestTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:')
        self.c.row_factory=sqlite3.Row
        storage.initialize(self.c)

    def tearDown(self):
        self.c.close()

    def test_league_setting_persists_and_validates(self):
        self.assertEqual(storage.current_league(self.c),'3.30')
        storage.set_league(self.c,'3.31')
        self.assertEqual(storage.current_league(self.c),'3.31')
        storage.initialize(self.c)
        self.assertEqual(storage.current_league(self.c),'3.31')
        with self.assertRaises(ValueError):
            storage.set_league(self.c,'3.31; DROP TABLE builds;')

    def test_replace_league_queries_without_modifying_search_config(self):
        old=['PoE 3.30 build','Path of Exile 3-30 leveling','PoE build']
        self.assertEqual(features.rendered_queries(old,'3.31'), ['PoE 3.31 build','Path of Exile 3.31 leveling','PoE build 3.31'])
        self.assertEqual(old[0],'PoE 3.30 build')

    def test_title_conflicts_filter(self):
        self.assertTrue(features.title_conflicts_with_league('PoE 3.29 lightning strike guide','3.30'))
        self.assertFalse(features.title_conflicts_with_league('PoE 3.30 lightning strike guide','3.30'))
        self.assertTrue(features.mentions_league('PoE guide','Path of Exile 3.30','3.30'))
        self.assertFalse(features.mentions_league('PoE 3.29 guide','old 3.29 league','3.30'))

    def test_digest_rolling_24h_and_old_db_migration(self):
        now=datetime(2026,11,12,20,0,tzinfo=timezone.utc)
        recent=datetime(2026,11,12,17,0,tzinfo=timezone.utc).isoformat()
        stale=datetime(2026,11,10,17,0,tzinfo=timezone.utc).isoformat()
        self.c.execute('INSERT INTO videos VALUES (?,?,?,?,?)',('aaaBBB11122','3.30 RF Slayer','https://youtu.be/aaaBBB11122',recent,recent))
        self.c.execute('INSERT INTO builds(fingerprint,canonical_title,first_video_id,created_at,league) VALUES(?,?,?,?,?)', ('league:3.30|rf', 'RF Slayer', 'aaaBBB11122',recent,'3.30'))
        self.c.execute('INSERT INTO video_metadata VALUES(?,?,?,?)',('aaaBBB11122','Righteous Fire','Slayer','Build'))
        self.c.execute('INSERT INTO videos VALUES (?,?,?,?,?)',('cccDDD11122','Old 3.30','https://youtu.be/cccDDD11122',stale,stale))
        self.c.execute('INSERT INTO builds(fingerprint,canonical_title,first_video_id,created_at,league) VALUES(?,?,?,?,?)', ('league:3.30|old','Old','cccDDD11122',stale,'3.30'))
        self.c.execute('INSERT INTO videos VALUES (?,?,?,?,?)',('eeeFFF11122','3.31 RF','https://youtu.be/eeeFFF11122',recent,recent))
        self.c.execute('INSERT INTO builds(fingerprint,canonical_title,first_video_id,created_at,league) VALUES(?,?,?,?,?)', ('league:3.31|rf','New league RF','eeeFFF11122',recent,'3.31'))
        self.c.commit()
        start,end=features.digest_window(now)
        entries=storage.digest_builds(self.c,'3.30',start,end)
        self.assertEqual(len(entries),1)
        self.assertEqual(entries[0]['skill'],'Righteous Fire')
        storage.initialize(self.c)
        self.assertEqual(len(storage.digest_builds(self.c,'3.30',start,end)),1)

    def test_daily_digest_sent_once_per_date(self):
        now=datetime(2026,11,12,19,0,tzinfo=timezone.utc)
        local=now.astimezone(ZoneInfo('Europe/Warsaw'))
        day=local.date().isoformat()
        self.assertTrue(features.digest_due(now,'20:00',None))
        storage.mark_digest_sent(self.c,123,day,sent_at=now)
        self.assertTrue(storage.digest_sent_date(self.c,123,day))
        self.assertFalse(features.digest_due(now,'20:00',day))
        self.assertFalse(storage.digest_sent_date(self.c,123,'2026-11-13'))

    def test_digest_time_is_polish_even_when_dst_changes(self):
        winter=datetime(2026,11,12,18,30,tzinfo=timezone.utc)
        summer=datetime(2026,7,12,18,30,tzinfo=timezone.utc)
        self.assertFalse(features.digest_due(winter,'20:00',None))
        self.assertTrue(features.digest_due(summer,'20:00',None))

    def test_mobalytics_buttons_only_poe(self):
        good=['https://mobalytics.gg/poe/builds/example','https://www.mobalytics.gg/poe/planner/builds/x','https://mobalytics.gg/poe']
        bad=['https://mobalytics.gg/lol/builds/akali', 'https://evil-mobalytics.gg/poe/builds','https://mobalytics.gg.evil.com/poe','https://mobalytics.gg/poe2/builds', 'javascript:alert(1)']
        for url in good: self.assertTrue(features.mobalytics_poe_url(url),url)
        for url in bad: self.assertFalse(features.mobalytics_poe_url(url),url)

    def test_legacy_build_migration_assigns_default_league(self):
        c=sqlite3.connect(':memory:')
        c.execute('CREATE TABLE builds(fingerprint TEXT PRIMARY KEY, canonical_title TEXT, first_video_id TEXT, created_at TEXT)')
        c.execute('INSERT INTO builds VALUES(?,?,?,?)', ('old','Old PoE 3.30','test','2026-11-12T00:00:00+00:00'))
        c.commit()
        storage.initialize(c)
        self.assertEqual(c.execute('SELECT league FROM builds WHERE fingerprint=?',('old',)).fetchone()[0],'3.30')
        c.close()

if __name__=='__main__': unittest.main()
