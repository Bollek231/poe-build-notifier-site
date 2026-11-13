"""v0.6.2b: dual-backend translation tests, all HTTP requests mocked."""
import sqlite3
import unittest
from datetime import datetime, timezone
import enhancements
import runtime_settings
import storage
import translation_providers as tr

class Response:
    def __init__(self, data, status=200):
        self.data,self.status=data,status
    async def __aenter__(self): return self
    async def __aexit__(self,*args):return False
    async def json(self,**kwargs):return self.data

class Session:
    def __init__(self,data,status=200):
        self.data,self.status=data,status
        self.calls=[]
    def get(self,url,**kwargs):
        self.calls.append(('GET',url,kwargs))
        return Response(self.data,self.status)
    def post(self,url,**kwargs):
        self.calls.append(('POST',url,kwargs))
        return Response(self.data,self.status)

class TranslationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.c=sqlite3.connect(':memory:')
        self.c.row_factory=sqlite3.Row
        storage.initialize(self.c)
        tr.init(self.c)
        self.now=datetime(2026,11,13,12,0,tzinfo=timezone.utc)
        self.title='Świetny build dla początkujących'
    async def asyncTearDown(self):self.c.close()

    async def test_mymemory_is_keyless_and_cached(self):
        ses=Session({'responseStatus':200,'responseData':{'translatedText':'Great beginner build'}})
        a=await tr.translate_to_english(ses,self.c,self.title,provider='mymemory',
            enabled=True,source_language='pl',now=self.now)
        b=await tr.translate_to_english(ses,self.c,self.title,provider='mymemory',
            enabled=True,source_language='pl',now=self.now)
        self.assertEqual(a,b)
        self.assertEqual(a,'Great beginner build')
        self.assertEqual(len(ses.calls),1)
        self.assertEqual(ses.calls[0][2]['params']['langpair'],'pl|en')
        self.assertNotIn('key',ses.calls[0][2]['params'])

    async def test_google_key_is_in_header_not_url(self):
        ses=Session({'data':{'translations':[{'translatedText':'Excellent build'}]}})
        a=await tr.translate_to_english(ses,self.c,self.title,provider='google',
            google_api_key='secret',enabled=True,source_language='pl',now=self.now)
        self.assertEqual(a,'Excellent build')
        self.assertEqual(ses.calls[0][0],'POST')
        self.assertEqual(ses.calls[0][2]['headers']['X-Goog-Api-Key'],'secret')
        self.assertNotIn('secret',ses.calls[0][1])

    async def test_provider_cache_separation(self):
        a=Session({'responseStatus':200,'responseData':{'translatedText':'MyMemory'}})
        b=Session({'data':{'translations':[{'translatedText':'Google'}]}})
        self.assertEqual(await tr.translate_to_english(a,self.c,self.title,
            provider='mymemory',enabled=True,source_language='pl',now=self.now),'MyMemory')
        self.assertEqual(await tr.translate_to_english(b,self.c,self.title,
            provider='google',google_api_key='secret',enabled=True,
            source_language='pl',now=self.now),'Google')

    async def test_fail_open_without_google_key_or_mymemory_availability(self):
        empty=Session({})
        self.assertEqual(await tr.translate_to_english(empty,self.c,self.title,
            provider='google',enabled=True,source_language='pl',now=self.now),self.title)
        self.assertFalse(empty.calls)
        down=Session({},429)
        self.assertEqual(await tr.translate_to_english(down,self.c,self.title,
            provider='mymemory',enabled=True,source_language='pl',now=self.now),self.title)

    async def test_500_byte_mymemory_limit(self):
        ses=Session({})
        source='あ'*167
        self.assertEqual(await tr.translate_to_english(ses,self.c,source,
            provider='mymemory',enabled=True,source_language='ja',now=self.now),source)
        self.assertFalse(ses.calls)

    async def test_char_limit(self):
        self.c.execute('INSERT INTO translation_requests_v2(provider,attempted_at,source_chars) VALUES(?,?,?)',
            ('mymemory',self.now.isoformat(),4490))
        self.c.commit()
        ses=Session({})
        self.assertEqual(await tr.translate_to_english(ses,self.c,self.title,
            provider='mymemory',enabled=True,source_language='pl',now=self.now),self.title)
        self.assertFalse(ses.calls)

    async def test_email_optional(self):
        ses=Session({'responseStatus':200,'responseData':{'translatedText':'Translated'}})
        await tr.translate_to_english(ses,self.c,self.title,provider='mymemory',
            enabled=True,source_language='pl',contact_email='admin@example.org',now=self.now)
        self.assertEqual(ses.calls[0][2]['params']['de'],'admin@example.org')

class VersionTests(unittest.TestCase):
    def test_version_b(self):
        self.assertEqual(enhancements.VERSION,'0.6.4d')
        self.assertTrue(enhancements.is_newer('0.6.2b','0.6.2'))
        self.assertFalse(enhancements.is_newer('0.6.2','0.6.2b'))
        self.assertTrue(enhancements.is_newer('0.6.3','0.6.2b'))
        self.assertIsNone(enhancements.parse_version('0.6.2b!'))
    def test_provider_setting(self):
        self.assertEqual(runtime_settings.parse_value('translation_provider',' GOOGLE '),'google')
        self.assertEqual(runtime_settings.parse_value('translation_provider','mymemory'),'mymemory')
        for wrong in ('auto','paid','none'):
            with self.assertRaises(ValueError):
                runtime_settings.parse_value('translation_provider',wrong)
