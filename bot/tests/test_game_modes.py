"""Regression tests for PoE Build Notifier v0.6.0 (offline, no Discord token)."""
import ast
import sqlite3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import game_modes,storage,features

source=(Path(__file__).resolve().parents[1]/'main.py').read_text(encoding='utf8')
tree=ast.parse(source)
names={'norm','find_term','identify','classify','fingerprint','extract_links'}
functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
ns={'re':__import__('re'),'features':features,'game_modes':game_modes,
    'urlparse':__import__('urllib.parse',fromlist=['urlparse']).urlparse}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'SKILLS','ASCENDANCIES','BUILD_SIGNALS'}:
        ns[node.targets[0].id]=ast.literal_eval(node.value)
exec(compile(ast.Module(body=functions,type_ignores=[]),'main_logic.py','exec'),ns)


class GameModeTests(unittest.TestCase):
    def test_default_and_aliases(self):
        self.assertEqual(game_modes.DEFAULT_POE2_VERSION,'1.0')
        for v in ('poe2','PoE 2','pathofexile2','2'):
            self.assertEqual(game_modes.normalize_game(v),'poe2')
        self.assertIsNone(game_modes.normalize_game('anothergame'))

    def test_independent_league_versions_persist(self):
        c=sqlite3.connect(':memory:');c.row_factory=sqlite3.Row
        storage.initialize(c)
        self.assertEqual(storage.current_game(c),'poe1')
        self.assertEqual(storage.current_game_version(c,'poe2'),'1.0')
        storage.set_league(c,'3.31')
        storage.set_game(c,'poe2')
        storage.set_game_version(c,'poe2','1.1')
        storage.initialize(c)
        self.assertEqual(storage.current_game(c),'poe2')
        self.assertEqual(storage.current_game_version(c,'poe1'),'3.31')
        self.assertEqual(storage.current_game_version(c,'poe2'),'1.1')
        storage.cleanup(c,7)
        self.assertEqual(storage.current_game_version(c,'poe2'),'1.1')
        c.close()

    def test_queries_explicitly_target_1_0(self):
        queries=game_modes.target_queries('1.0')
        self.assertGreaterEqual(len(queries),6)
        self.assertTrue(all('1.0' in query for query in queries))
        self.assertTrue(all('PoE2' in q or 'PoE 2' in q or 'Path of Exile 2' in q for q in queries))
        self.assertFalse(any('0.5' in q or '3.30' in q for q in queries))
        self.assertEqual(game_modes.target_queries('1.1',['PoE 2 {version} build']),['PoE 2 1.1 build'])

    def test_accept_new_poe2_1_0_builds(self):
        for title in ('PoE2 1.0 league starter build','Path of Exile 2 1.0 Gas Grenade build guide',
                      'PoE 2 1.0 leveling build','Path of Exile II 1.0 Spark Build'):
            with self.subTest(title=title):
                self.assertTrue(game_modes.is_target_poe2_guide(title,''))
                self.assertIsNotNone(ns['classify'](title,'',[],'1.0','poe2'))

    def test_block_old_versions_and_news(self):
        titles=('PoE2 0.5.5 build guide','PoE 2 0.3.1 League Starter',
                'PoE 2 1.0 build compared to old 0.5.5','PoE2 1.1 endgame build',
                'PoE 2 1.0 Patch Notes','PoE 2 1.0 build tier list',
                'PoE 2 best build with no version','PoE 1 1.0 build guide',
                'PoE 2 1.0 reupload old build')
        for title in titles:
            with self.subTest(title=title):
                self.assertFalse(game_modes.is_target_poe2_guide(title,''))
                self.assertIsNone(ns['classify'](title,'',[],'1.0','poe2'))

    def test_version_conflict_beats_description(self):
        self.assertFalse(game_modes.is_target_poe2_guide('PoE2 0.5.5 Witch build','The future is PoE 2 1.0'))
        self.assertTrue(game_modes.is_target_poe2_guide('PoE 2 Gas Grenade build guide','Updated for patch 1.0 in PoE 2.'))
        self.assertFalse(game_modes.is_target_poe2_guide('PoE 2 Gas Grenade build guide','Unversioned guide.'))

    def test_discord_filter_settings_are_independent(self):
        c=sqlite3.connect(':memory:');c.row_factory=sqlite3.Row;storage.initialize(c)
        storage.set_filters(c,{'skill':'Lightning Strike'},'poe1')
        storage.set_filters(c,{'skill':'Gas Grenade'},'poe2')
        self.assertEqual(storage.get_filters(c,'poe1'),{'skill':'Lightning Strike'})
        self.assertEqual(storage.get_filters(c,'poe2'),{'skill':'Gas Grenade'})
        storage.cleanup(c,7)
        self.assertEqual(storage.get_filters(c,'poe2'),{'skill':'Gas Grenade'})
        c.close()

    def test_mobalytics_poe2_url(self):
        self.assertTrue(features.mobalytics_poe_url('https://mobalytics.gg/poe-2/builds/abc'))
        self.assertEqual(ns['extract_links']('https://mobalytics.gg/poe-2/builds/abc')['Mobalytics'],
                         'https://mobalytics.gg/poe-2/builds/abc')
        self.assertFalse(features.mobalytics_poe_url('https://mobalytics.gg/lol/builds/abc'))

    def test_poe1_kept_intact(self):
        self.assertIsNotNone(ns['classify']('PoE 3.30 Lightning Strike build guide','',[],'3.30','poe1'))
        self.assertIsNone(ns['classify']('PoE 3.30 Lightning Strike build guide','',[],'1.0','poe2'))

    def test_commands_and_24h_age_window(self):
        self.assertIn("@bot.command(name='Game')",source)
        self.assertIn("storage.set_game(c,new)",source)
        self.assertIn("game_modes.target_queries(league",source)
        self.assertIn("MAX_VIDEO_AGE_HOURS = max(1, int(os.getenv('MAX_VIDEO_AGE_HOURS', '24')))",source)
        self.assertIn("'publishedAfter': (utc_now() - timedelta(hours=MAX_VIDEO_AGE_HOURS))",source)
        self.assertIn("MAX_VIDEO_AGE_HOURS) <= published <= utc_now() + timedelta(minutes=2)",source)
        self.assertNotIn('await message.delete(',source)


if __name__=='__main__':unittest.main()
