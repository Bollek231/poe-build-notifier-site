import sqlite3
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import storage

class QuotaTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:')
        storage.initialize(self.c)
    def tearDown(self):
        self.c.close()
    def test_daily_429_search_list_detection(self):
        p={'error':{'code':429,'message':"Quota exceeded for quota metric 'Search Queries' and limit 'Search Queries per day' of service 'youtube.googleapis.com'"}}
        self.assertTrue(storage.is_daily_search_quota_error(429,p))
        self.assertFalse(storage.is_daily_search_quota_error(200,p))
        self.assertFalse(storage.is_daily_search_quota_error(429,{'error':{'message':'Too many requests per minute'}}))
        self.assertFalse(storage.is_daily_search_quota_error(403,{'error':{'message':'Billing is disabled'}}))
    def test_reset_winter_poland_9(self):
        now=datetime(2026,11,12,20,0,tzinfo=timezone.utc)
        reset=storage.next_search_quota_reset(now=now)
        self.assertEqual(reset,datetime(2026,11,13,8,0,tzinfo=timezone.utc))
        self.assertEqual(reset.astimezone(ZoneInfo('Europe/Warsaw')).hour,9)
    def test_reset_summer_poland_9(self):
        now=datetime(2026,7,5,20,0,tzinfo=timezone.utc)
        reset=storage.next_search_quota_reset(now=now)
        self.assertEqual(reset,datetime(2026,7,6,7,0,tzinfo=timezone.utc))
        self.assertEqual(reset.astimezone(ZoneInfo('Europe/Warsaw')).hour,9)
    def test_pause_persists_restart_and_expires(self):
        now=datetime(2026,11,12,20,0,tzinfo=timezone.utc)
        reset=storage.next_search_quota_reset(now=now)
        storage.begin_quota_pause(self.c,reset)
        self.assertEqual(storage.quota_pause(self.c,now=now),(reset,False))
        storage.mark_quota_notice_sent(self.c)
        self.assertEqual(storage.quota_pause(self.c,now=now),(reset,True))
        self.assertIsNone(storage.quota_pause(self.c,now=reset+timedelta(seconds=1)))
        self.assertIsNone(storage.quota_pause(self.c,now=now))
    def test_migration_is_idempotent(self):
        storage.initialize(self.c)
        storage.initialize(self.c)
        self.assertIsNone(storage.quota_pause(self.c))
    def test_code_does_not_delete_discord_posts(self):
        source=(Path(__file__).resolve().parents[1]/'main.py').read_text()
        self.assertNotIn('fetch_message(',source)
        self.assertNotIn('message.delete(',source)
        self.assertIn('except DailySearchQuotaExceeded:',source)
        self.assertIn('await announce_quota_pause(c, quota_reset)',source)
if __name__=='__main__':unittest.main()
