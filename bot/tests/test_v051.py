"""Offline v0.5.1 regression tests: no tokens, Discord, or external HTTP needed."""
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import enhancements as e
import storage
import backups
import services


class FeatureTests(unittest.TestCase):
    def test_version_number_and_comparison(self):
        self.assertEqual(e.VERSION,'0.6.2b')
        self.assertTrue(e.is_newer('v0.6.3'))
        self.assertFalse(e.is_newer('0.6.0'))
        self.assertFalse(e.is_newer('bad'))
        self.assertFalse(e.is_newer('0.5.0'))
        self.assertFalse(e.is_newer('0.5.99','0.6.0'))

    def test_quota_budget_schedule(self):
        d=datetime(2026,11,13,9,0,tzinfo=timezone.utc)
        self.assertGreaterEqual(e.auto_query_allocation(72,24,d,2,6),1)
        self.assertLessEqual(e.auto_query_allocation(72,24,d,2,6),6)
        self.assertEqual(e.auto_query_allocation(24,24,d,2,6),0)
        self.assertEqual(e.auto_query_allocation(0,0,d,2,6),0)
        self.assertEqual(e.auto_query_allocation(27,24,d,2,6),1)
        self.assertLessEqual(e.auto_query_allocation(72,24,d,2,6),48)

    def test_quota_reset_near_midnight(self):
        local=datetime(2026,11,12,23,30,tzinfo=e.PACIFIC)
        self.assertEqual(e.auto_query_allocation(30,24,local,2,6),6)
        self.assertEqual(e.auto_query_allocation(30,24,local,2,2),2)

    def test_round_robin_queries(self):
        q=['a','b','c','d']
        chosen,c=e.rotate_queries(q,2,0)
        self.assertEqual((chosen,c),(['a','b'],2))
        self.assertEqual(e.rotate_queries(q,2,c),(['c','d'],0))
        self.assertEqual(e.rotate_queries(q,0,c),([],2))

    def test_channel_id_validation(self):
        channel='UC'+'A'*22
        self.assertEqual(e.youtube_channel_id(channel),channel)
        self.assertEqual(e.youtube_channel_id('https://www.youtube.com/channel/'+channel),channel)
        self.assertIsNone(e.youtube_channel_id('https://evil.youtube.com/channel/'+channel))
        self.assertIsNone(e.youtube_channel_id('https://www.youtube.com/@not-a-channel-id'))
        self.assertIsNone(e.youtube_channel_id('UCmalicious'))

    def test_filter_values(self):
        self.assertEqual(e.validate_filter('skill','lightning strike',['Lightning Strike'],[]),'Lightning Strike')
        self.assertEqual(e.validate_filter('mode','ssf',[],[]),'SSF')
        self.assertEqual(e.validate_filter('stage','Starter',[],[]),'starter')
        self.assertEqual(e.validate_filter('class','RANGER',[],[]),'Ranger')
        self.assertIsNone(e.validate_filter('mode','all',[],[]))
        with self.assertRaises(ValueError):e.validate_filter('mode','unknown',[],[])

    def test_strict_filters_do_not_guess_mode_or_class(self):
        title='PoE 3.31 Lightning Strike Deadeye League Starter build'
        base={'skill':'Lightning Strike','ascendancy':'Deadeye','class':'Ranger','stage':'starter'}
        self.assertTrue(e.matches_filters(title,'', 'Lightning Strike','Deadeye','League Starter',base))
        self.assertFalse(e.matches_filters(title,'','Lightning Strike','Slayer','League Starter',base))
        self.assertFalse(e.matches_filters(title,'','Lightning Strike','Deadeye','Endgame',base))
        self.assertFalse(e.matches_filters(title,'','Lightning Strike','Deadeye','League Starter',{'mode':'SC'}))
        self.assertTrue(e.matches_filters(title+' (SSF)','','Lightning Strike','Deadeye','League Starter',{'mode':'SSF'}))
        self.assertTrue(e.matches_filters(title+' HC','','Lightning Strike','Deadeye','League Starter',{'mode':'HC'}))

    def test_url_validation_no_ssrf(self):
        good=['https://pobb.in/abc','https://mobalytics.gg/poe/builds/123','https://maxroll.gg/poe/build-guides/123']
        bad=['http://pobb.in/a','https://pobb.in.evil.com/a','https://127.0.0.1/foo',
             'https://localhost/private','file:///etc/passwd','https://user:pass@pobb.in/a',
             'https://evil.com','https://pobb.in:444/path']
        self.assertTrue(all(e.sane_external_url(x) for x in good))
        self.assertTrue(all(not e.sane_external_url(x) for x in bad))

    def test_links_merged_without_removal(self):
        old={'Path of Building':'https://pobb.in/abc'}
        new={'Mobalytics':'https://mobalytics.gg/poe/builds/x'}
        self.assertTrue(e.links_changed(old,new))
        self.assertFalse(e.links_changed(old,{}))
        self.assertEqual(e.merged_links(old,new),{**old,**new})

    def test_main_code_non_destructive(self):
        code=(Path(__file__).resolve().parents[1]/'main.py').read_text()
        self.assertIn('await message.edit(view=buttons_from_links(merged,vid))',code)
        self.assertNotIn('await message.delete(',code)
        self.assertIn("@bot.command(name='Version')",code)
        self.assertIn("@bot.command(name='Filter')",code)
        self.assertIn("@bot.command(name='BlockChannel')",code)
        self.assertIn('storage.record_post(',code)
        self.assertIn('storage.quota_pause(',code)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.c=sqlite3.connect(':memory:');self.c.row_factory=sqlite3.Row;storage.initialize(self.c)

    def tearDown(self):self.c.close()

    def test_rules_survive_reinitialize(self):
        channel='UC'+'A'*22
        storage.put_channel_rule(self.c,channel,'block')
        self.assertEqual(storage.channel_rule(self.c,channel),'block')
        storage.put_channel_rule(self.c,channel,'allow')
        storage.initialize(self.c)
        self.assertEqual(storage.channel_rule(self.c,channel),'allow')
        self.assertEqual(len(storage.all_channel_rules(self.c)),1)
        self.assertTrue(storage.delete_channel_rule(self.c,channel))
        self.assertIsNone(storage.channel_rule(self.c,channel))

    def test_rules_validation(self):
        with self.assertRaises(ValueError):storage.put_channel_rule(self.c,'bad','block')
        with self.assertRaises(ValueError):storage.put_channel_rule(self.c,'UC'+'A'*22,'other')

    def test_filter_storage_survives_retention_cleanup(self):
        storage.set_filters(self.c,{'mode':'SSF','skill':'Spark'})
        storage.cleanup(self.c,7)
        storage.initialize(self.c)
        self.assertEqual(storage.get_filters(self.c),{'mode':'SSF','skill':'Spark'})

    def test_post_tracking_and_retention_only(self):
        now=datetime(2026,11,13,12,0,tzinfo=timezone.utc)
        storage.record_post(self.c,'Abc123',123,456,{'Maxroll':'https://maxroll.gg/poe/test'},now=now)
        rows=storage.refresh_candidates(self.c,cutoff=now+timedelta(hours=8))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['message_id'],'456')
        self.assertEqual(json.loads(rows[0]['links_json']),{'Maxroll':'https://maxroll.gg/poe/test'})
        storage.cleanup(self.c,7,now=now+timedelta(days=8))
        self.assertEqual(self.c.execute('select count(*) from posted_messages').fetchone()[0],0)
        self.assertTrue('discord_posts_tracking' in storage.cleanup(self.c,7))

    def test_alert_rate_limit(self):
        t=datetime(2026,11,13,tzinfo=timezone.utc)
        self.assertTrue(storage.alert_allowed(self.c,'restart',now=t))
        storage.record_alert(self.c,'restart',now=t)
        self.assertFalse(storage.alert_allowed(self.c,'restart',now=t+timedelta(minutes=30)))
        self.assertTrue(storage.alert_allowed(self.c,'restart',now=t+timedelta(minutes=62)))

    def test_link_state_cache(self):
        storage.store_link_state(self.c,'https://pobb.in/example','uncertain')
        self.assertEqual(storage.cached_link_state(self.c,'https://pobb.in/example'),'uncertain')
        self.assertIsNone(storage.cached_link_state(self.c,'https://pobb.in/notthere'))


class BackupTests(unittest.TestCase):
    def test_online_backup_preserves_tables_and_no_env(self):
        with tempfile.TemporaryDirectory() as d:
            work=Path(d)
            dbfile=work/'live.sqlite3'
            with sqlite3.connect(dbfile) as c:
                storage.initialize(c)
                storage.set_setting(c,'target_league','3.31')
            (work/'.env').write_text('DISCORD_TOKEN=PLACEHOLDER_ONLY_FOR_TESTS')
            stamp=datetime(2026,11,13,9,0,tzinfo=timezone.utc)
            dest,created=backups.backup_database(dbfile,work/'backups',now=stamp)
            self.assertTrue(created)
            with sqlite3.connect(dest) as c:
                self.assertEqual(storage.get_setting(c,'target_league','3.30'),'3.31')
            self.assertFalse((work/'backups'/'.env').exists())
            self.assertEqual(len(list((work/'backups').iterdir())),1)
            _,again=backups.backup_database(dbfile,work/'backups',now=stamp)
            self.assertFalse(again)
            self.assertTrue((work/'.env').exists())

    def test_backup_rotation_and_never_delete_database(self):
        with tempfile.TemporaryDirectory() as d:
            work=Path(d);dbfile=work/'live.sqlite3'
            with sqlite3.connect(dbfile) as c:storage.initialize(c)
            for n in range(5):
                day=datetime(2026,11,11+n,12,0,tzinfo=timezone.utc)
                backups.backup_database(dbfile,work/'backups',keep=3,now=day)
            self.assertEqual(len(list((work/'backups').glob('*.sqlite3'))),3)
            self.assertTrue(dbfile.exists())


class MockResponse:
    def __init__(self,status,body='',headers=None):self.status=status;self.body=body;self.headers=headers or {}
    async def __aenter__(self):return self
    async def __aexit__(self,*args):return False
    async def text(self):return self.body


class MockSession:
    def __init__(self,status,body='',second=None):self.status=status;self.body=body;self.second=second;self.head_calls=0;self.get_calls=0
    def head(self,*args,**kwargs):
        self.head_calls+=1
        self.kwargs=kwargs
        return MockResponse(self.status)
    def get(self,*args,**kwargs):
        self.get_calls+=1
        return MockResponse(self.second if self.second is not None else self.status,self.body)


class RemoteTests(unittest.IsolatedAsyncioTestCase):
    async def test_link_200_404_and_cloudflare(self):
        for status,expected in [(200,'ok'),(404,'dead'),(410,'dead'),(403,'uncertain'),(302,'uncertain')]:
            session=MockSession(status)
            self.assertEqual(await services.check_guide_link(session,'https://pobb.in/test'),expected)
            self.assertEqual(session.head_calls,1)
            self.assertFalse(session.kwargs['allow_redirects'])

    async def test_link_fallback_405(self):
        session=MockSession(405,second=200)
        self.assertEqual(await services.check_guide_link(session,'https://pobb.in/test'),'ok')
        self.assertEqual(session.get_calls,1)

    async def test_invalid_url_never_requested(self):
        session=MockSession(200)
        self.assertEqual(await services.check_guide_link(session,'https://attacker.invalid/path'),'dead')
        self.assertEqual(session.head_calls,0)

    async def test_version_response(self):
        session=MockSession(200,'0.5.2\n')
        self.assertEqual(await services.latest_public_version(session),'0.5.2')
        session=MockSession(200,'TOKEN=abc')
        self.assertIsNone(await services.latest_public_version(session))


if __name__=='__main__':unittest.main()
