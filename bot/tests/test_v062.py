import asyncio
import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import community
import storage

ID='dQw4w9WgXcQ'
ID2='N12AbcDeFgH'

class CommunityFeatureTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:')
        self.c.row_factory=sqlite3.Row
        storage.initialize(self.c)
        community.init(self.c)
        self.now=datetime(2026,11,13,7,tzinfo=timezone.utc)

    def tearDown(self):self.c.close()

    def test_quiet_cross_midnight(self):
        self.assertTrue(community.is_quiet(self.now,'23:00','08:30'))
        self.assertFalse(community.is_quiet(self.now,'21:00','07:00'))
        self.assertTrue(community.is_quiet(self.now,'08:00','09:00'))
    def test_quiet_same_day(self):
        self.assertTrue(community.is_quiet(self.now,'07:00','09:00'))
        self.assertFalse(community.is_quiet(self.now,'12:00','14:00'))
    def test_invalid_quiet(self):
        for a,b in [('24:00','08:00'),('10:00','10:00'),('10:15','oops')]:
            with self.assertRaises(ValueError):community.validate_quiet(a,b)
    def test_quiet_saved(self):
        community.set_quiet(self.c,'23:00','08:00')
        self.assertEqual(community.get_quiet(self.c),('23:00','08:00'))
        community.set_quiet(self.c)
        self.assertEqual(community.get_quiet(self.c),('',''))
    def test_pause_and_resume(self):
        community.set_pause(self.c,'6h',self.now)
        self.assertIsNotNone(community.pause_until(self.c,self.now))
        self.assertIsNone(community.pause_until(self.c,self.now+timedelta(hours=7)))
        community.set_pause(self.c,'forever')
        self.assertEqual(community.pause_until(self.c),'forever')
        community.clear_pause(self.c)
        self.assertIsNone(community.pause_until(self.c))
    def test_pause_rejects_bad_input(self):
        for duration in ['-1h','100h','0h','python','1d']:
            with self.assertRaises(ValueError):community.set_pause(self.c,duration)
    def test_saved_user_isolation(self):
        self.assertTrue(community.saved_toggle(self.c,100,ID))
        self.assertTrue(community.saved_toggle(self.c,200,ID))
        self.assertFalse(community.saved_toggle(self.c,100,ID))
        self.assertEqual(community.saved_list(self.c,100),[])
        self.assertEqual(community.saved_list(self.c,200),[ID])
        self.assertEqual(community.saved_remove(self.c,200),1)
    def test_saved_video_id_validation(self):
        for bad in ['x'*200,'a b','https://youtube.com','../secrets']:
            with self.assertRaises(ValueError):community.saved_toggle(self.c,1,bad)
    def test_queue_processing(self):
        self.assertTrue(community.queue_video(self.c,ID,'poe2','1.0','New build',self.now.isoformat(),self.now))
        self.assertFalse(community.queue_video(self.c,ID,'poe2','1.0','New build',self.now.isoformat(),self.now))
        rows=community.queued(self.c)
        self.assertEqual(len(rows),1)
        community.finish_queue(self.c,rows,self.now)
        self.assertFalse(community.queued(self.c))
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM videos').fetchone()[0],1)
    def test_trend_rank_with_observations(self):
        community.record_views(self.c,{ID:100,ID2:500},self.now)
        updated=self.now+timedelta(hours=2)
        scores=community.trend_rank(self.c,{ID:400,ID2:550},updated)
        self.assertEqual(scores[0][0],ID)
        self.assertAlmostEqual(scores[0][1],150)
        self.assertEqual(scores[1][2],50)
    def test_trend_first_baseline(self):
        scores=community.trend_rank(self.c,{ID:42},self.now)
        self.assertFalse(scores[0][4])
    def test_cleanup_only_caches(self):
        community.saved_toggle(self.c,100,ID)
        community.record_views(self.c,{ID:100},self.now-timedelta(days=8))
        community.cleanup(self.c,7,self.now)
        self.assertFalse(self.c.execute('SELECT * FROM video_trends').fetchall())
        self.assertEqual(community.saved_list(self.c,100),[ID])

class TranslationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.c=sqlite3.connect(':memory:')
        community.init(self.c)
        self.now=datetime(2026,11,13,7,tzinfo=timezone.utc)
    async def asyncTearDown(self):self.c.close()
    async def test_no_key_no_request(self):
        result=await community.translate_to_english(None,self.c,'Przykład','',enabled=True)
        self.assertEqual(result,'Przykład')
    async def test_disabled_no_request(self):
        result=await community.translate_to_english(None,self.c,'Przykład','secret',enabled=False)
        self.assertEqual(result,'Przykład')
    async def test_daily_limit_fallback(self):
        for _ in range(3):self.c.execute('INSERT INTO translation_usage(attempted_at) VALUES(?)',(self.now.isoformat(),))
        self.c.commit()
        result=await community.translate_to_english(None,self.c,'Przykład','secret',enabled=True,max_daily=3,now=self.now)
        self.assertEqual(result,'Przykład')
    async def test_cache_no_network(self):
        source='Un build en espagnol'
        self.c.execute('INSERT INTO title_translations VALUES(?,?,?)',(community.title_hash(source),'A build in Spanish',self.now.isoformat()))
        self.c.commit()
        result=await community.translate_to_english(None,self.c,source,'secret',enabled=True,now=self.now)
        self.assertEqual(result,'A build in Spanish')

if __name__=='__main__':unittest.main()
