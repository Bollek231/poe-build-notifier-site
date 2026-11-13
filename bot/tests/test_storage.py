import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import storage

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.connection = sqlite3.connect(str(Path(self.tmp.name) / 'poe330_seen.sqlite3'))
        self.connection.row_factory = sqlite3.Row
        storage.initialize(self.connection)

    def tearDown(self):
        self.connection.close()
        self.tmp.cleanup()

    def test_seven_day_retention_for_api_data_only(self):
        now = datetime(2026, 11, 12, tzinfo=timezone.utc)
        old = (now-timedelta(days=8)).isoformat()
        new = (now-timedelta(hours=4)).isoformat()
        for vid,dt in [('old',old),('new',new)]:
            self.connection.execute('INSERT INTO videos VALUES (?,?,?,?,?)', (vid,vid,f'https://youtu.be/{vid}',dt,dt))
            self.connection.execute('INSERT INTO builds(fingerprint,canonical_title,first_video_id,created_at) VALUES (?,?,?,?)', (vid,vid,vid,dt))
            self.connection.execute('INSERT INTO video_metadata VALUES (?,?,?,?)', (vid,'Spark','Slayer','Build'))
            self.connection.execute('INSERT INTO search_log (searched_at,query,kind) VALUES(?,?,?)', (dt,'poe build','auto'))
            self.connection.execute('INSERT INTO api_usage (used_at,units,operation) VALUES(?,?,?)', (dt,1,'search.list'))
        self.connection.commit()
        result=storage.cleanup(self.connection,7,now=now)
        for table in ('videos','builds','video_metadata','search_log','api_usage'):
            self.assertEqual(self.connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0],1,table)
        self.assertEqual(result['videos'],1)

    def test_old_deletion_queue_cleared_only_locally(self):
        old_time=(datetime(2026,11,12,tzinfo=timezone.utc)-timedelta(days=10)).isoformat()
        self.connection.execute('INSERT INTO discord_posts VALUES (?,?,?)', ('543210987','123456789',old_time))
        self.connection.commit()
        stats=storage.cleanup(self.connection,7,now=datetime(2026,11,12,tzinfo=timezone.utc))
        self.assertEqual(stats['discord_posts_tracking'],1)
        self.assertEqual(self.connection.execute('SELECT COUNT(*) FROM discord_posts').fetchone()[0],0)

    def test_consent_record_without_role(self):
        storage.record_consent(self.connection,123,456,'2026-11-12-v2')
        self.assertTrue(storage.has_consent(self.connection,123,456,'2026-11-12-v2'))
        self.assertFalse(storage.has_consent(self.connection,123,456,'2026-11-12'))
        storage.revoke_consent(self.connection,123,456)
        self.assertFalse(storage.has_consent(self.connection,123,456,'2026-11-12-v2'))

    def test_migrate_prior_db_schema(self):
        self.connection.execute('INSERT INTO videos VALUES(?,?,?,?,?)',('abc','title','https://youtu.be/abc','2026-11-12T10:00:00+00:00','2026-11-12T10:00:00+00:00'))
        self.connection.commit()
        storage.initialize(self.connection)
        self.assertEqual(self.connection.execute('SELECT count(*) FROM videos').fetchone()[0],1)

    def test_never_delete_discord_messages_in_bot_code(self):
        source=(Path(__file__).resolve().parents[1] / 'main.py').read_text(encoding='utf8')
        self.assertNotIn('message.delete(',source)
        # v0.5.1 may FETCH an existing post to add new link buttons.
        # It must never delete/repost the message.
        self.assertNotIn('await message.delete(',source)
        self.assertIn('await message.edit(view=buttons_from_links(merged,vid))',source)
        self.assertNotIn('await cleanup_discord_posts(',source)
        self.assertNotIn('storage.track_post(',source)
        self.assertNotIn('OPT_IN_ROLE_ID',source)
        self.assertNotIn("@bot.command(name='Activate')",source)

    def test_lifetime_max_29_days(self):
        with self.assertRaises(ValueError):
            storage.cleanup(self.connection,30)

if __name__=='__main__':unittest.main()
