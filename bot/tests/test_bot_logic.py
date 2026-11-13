"""Exercise real pure main.py functions without Discord credentials or network."""
import ast
import re
import sqlite3
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import features,storage,game_modes,enhancements

source=(Path(__file__).resolve().parents[1]/'main.py').read_text(encoding='utf8')
tree=ast.parse(source)

names={'norm','find_term','identify','classify','fingerprint','duplicate','extract_links','format_digest_pages'}
functions=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names]
ns={'re':re,'urlparse':urlparse,'features':features,'game_modes':game_modes,'enhancements':enhancements,'SequenceMatcher':__import__('difflib').SequenceMatcher,'discord':None}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
        if node.targets[0].id in {'ASCENDANCIES','SKILLS','BUILD_SIGNALS'}:
            ns[node.targets[0].id]=ast.literal_eval(node.value)
exec(compile(ast.Module(body=functions,type_ignores=[]),'main_functions.py','exec'),ns)

class FakeEmbed:
    def __init__(self, title, description=None,color=None):
        self.title=title;self.description=description;self.footer=''
    def set_footer(self,*,text):self.footer=text

ns['discord']=SimpleNamespace(Embed=FakeEmbed,Color=SimpleNamespace(dark_purple=lambda:1),utils=SimpleNamespace(escape_markdown=lambda x:x.replace(']','\\]'),escape_mentions=lambda x:x))

class BotLogicTests(unittest.TestCase):
    def test_classification_tracks_target_league(self):
        signal='PoE 3.31 Lightning Strike Slayer league starter build'
        self.assertIsNotNone(ns['classify'](signal,'',[],'3.31'))
        self.assertIsNone(ns['classify'](signal,'',[],'3.30'))
        self.assertIsNone(ns['classify']('PoE 3.29 Lightning Strike build','See PoE 3.31 guide',['news'],'3.31'))
        self.assertIsNotNone(ns['classify']('PoE Lightning Strike Slayer build','This is for PoE 3.31, league starter!',[],'3.31'))

    def test_duplicates_are_separate_by_league_but_legacy_matches(self):
        c=sqlite3.connect(':memory:');c.row_factory=sqlite3.Row;storage.initialize(c)
        old_fp='skill:lightning strike|asc:slayer'
        c.execute('INSERT INTO builds(fingerprint,canonical_title,first_video_id,created_at,league) VALUES(?,?,?,?,?)',(old_fp,'old','abc','2026-11-12T00:00:00+00:00','3.30'))
        p30=ns['fingerprint']('PoE 3.30 lightning strike Slayer','Lightning Strike','Slayer','3.30')
        p31=ns['fingerprint']('PoE 3.31 lightning strike Slayer','Lightning Strike','Slayer','3.31')
        self.assertTrue(ns['duplicate'](c,p30,'3.30'))
        self.assertFalse(ns['duplicate'](c,p31,'3.31'))
        c.close()

    def test_poe_mobalytics_button_extraction(self):
        desc='See https://mobalytics.gg/poe/builds/abc and https://mobalytics.gg/lol/builds/xyz plus https://pobb.in/abcd.'
        links=ns['extract_links'](desc)
        self.assertEqual(links['Mobalytics'],'https://mobalytics.gg/poe/builds/abc')
        self.assertEqual(links['Path of Building'],'https://pobb.in/abcd')
        self.assertNotIn('Maxroll',links)

    def test_poeplanner_farming_link_extraction(self):
        desc=('Farming setup: https://poeplanner.com/a/AbC123 '
              'alternative https://www.poeplanner.com/a/other '
              'and https://pobb.in/example.')
        links=ns['extract_links'](desc)
        self.assertEqual(links['PoE Planner'],'https://poeplanner.com/a/AbC123')
        self.assertEqual(links['Path of Building'],'https://pobb.in/example')

    def test_poeplanner_rejects_lookalikes_and_unsafe_urls(self):
        desc=('Ignore https://poeplanner.com.evil.example/a/abc '
              'and https://fakepoeplanner.com/abc '
              'and http://poeplanner.com/a/no-tls '
              'and https://poeplanner.com:444/a/bad '
              'but keep https://www.poeplanner.com/atlas/valid?foo=bar.')
        links=ns['extract_links'](desc)
        self.assertEqual(links['PoE Planner'],
                         'https://www.poeplanner.com/atlas/valid?foo=bar')

    def test_daily_digest_format_under_discord_limits(self):
        rows=[]
        for i in range(80):
            rows.append({'canonical_title':'Lightning Strike Slayer build '*4,'skill':'Lightning Strike','ascendancy':'Slayer','classification':'League Starter','first_video_id':f'{i:011d}'})
        result=ns['format_digest_pages'](rows,'3.30','2026-11-12')
        self.assertGreater(len(result),1)
        self.assertTrue(all(len(e.description)<=4096 for e in result))
        self.assertEqual(sum(e.description.count('https://youtu.be/') for e in result),80)

if __name__=='__main__':unittest.main()
