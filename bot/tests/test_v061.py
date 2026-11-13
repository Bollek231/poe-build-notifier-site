"""v0.6.1: persisted bilingual preferences, safe settings and interaction security.

All tests run offline without Discord tokens or YouTube/Discord network calls.
"""
import ast
import sqlite3
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import storage, runtime_settings as settings, localization

DEFAULTS={
 'scan_interval_hours':2,'digest_time':'20:00','digest_enabled':True,
 'results_per_query':25,'send_delay_seconds':3.,'daily_search_budget':96,
 'reserved_searches':24,'video_age_hours':24,'link_refresh_hours':6,
 'links_check_enabled':True,'version_check_enabled':True,
 'version_check_hours':12,'link_refresh_limit':10,
}

class Version061Tests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(':memory:');self.c.row_factory=sqlite3.Row
  storage.initialize(self.c)
 def tearDown(self):self.c.close()

 def test_default_language_and_aliases(self):
  self.assertEqual(settings.get_language(self.c),'pl')
  for value in ('Polski','polish',' PL '):self.assertEqual(settings.normalize_language(value),'pl')
  for value in ('Angielski','English',' EN '):self.assertEqual(settings.normalize_language(value),'en')
  self.assertIsNone(settings.normalize_language('es'))
  self.assertIsNone(settings.normalize_language('fr'))

 def test_english_persists_after_reopening_database(self):
  self.assertEqual(settings.set_language(self.c,'english'),'en')
  self.assertEqual(settings.get_language(self.c),'en')
  storage.initialize(self.c)
  self.assertEqual(settings.get_language(self.c),'en')
  storage.cleanup(self.c,7)
  self.assertEqual(settings.get_language(self.c),'en')
  self.assertEqual(settings.set_language(self.c,'polski'),'pl')

 def test_defaults_and_validation(self):
  self.assertEqual(settings.snapshot(self.c,DEFAULTS),DEFAULTS)
  self.assertEqual(settings.parse_value('digest_time','08:09'),'08:09')
  self.assertEqual(settings.parse_value('scan_interval_hours','12'),12)
  self.assertEqual(settings.parse_value('send_delay_seconds','2.50'),2.5)
  self.assertTrue(settings.parse_value('digest_enabled','on'))
  self.assertFalse(settings.parse_value('digest_enabled','off'))

 def test_strict_rejects_unsafe_values(self):
  invalid=[('scan_interval_hours','0'),('scan_interval_hours','25'),
    ('scan_interval_hours','1.5'),('digest_time','24:00'),('digest_time','19:61'),
    ('digest_time','20:00; rm -rf'),('video_age_hours','25'),
    ('send_delay_seconds','0'),('send_delay_seconds','40'),
    ('results_per_query','100'),('daily_search_budget','10001'),
    ('version_check_hours','0'),('version_check_hours','73'),
    ('links_check_enabled','sometimes'),('digest_enabled',''),
    ('backup_dir','/tmp/hack'),('token','123'),('results_per_query','-1')]
  for key,value in invalid:
   with self.subTest(key=key,value=value),self.assertRaises(ValueError):
    settings.parse_value(key,value)

 def test_budget_invariants(self):
  with self.assertRaises(ValueError):settings.update_setting(self.c,DEFAULTS,'daily_search_budget','24')
  with self.assertRaises(ValueError):settings.update_setting(self.c,DEFAULTS,'reserved_searches','96')
  self.assertEqual(settings.update_setting(self.c,DEFAULTS,'reserved_searches','12')['reserved_searches'],12)
  self.assertEqual(settings.update_setting(self.c,DEFAULTS,'daily_search_budget','24')['daily_search_budget'],24)
  self.assertEqual(settings.snapshot(self.c,DEFAULTS)['reserved_searches'],12)

 def test_persistent_edit_does_not_overwrite_game_or_consent(self):
  storage.record_consent(self.c,123,456,'2026-11-12-v2')
  storage.set_game(self.c,'poe2')
  storage.set_game_version(self.c,'poe2','1.0')
  after=settings.update_setting(self.c,DEFAULTS,'scan_interval_hours','6')
  self.assertEqual(after['scan_interval_hours'],6)
  self.assertEqual(storage.current_game(self.c),'poe2')
  self.assertEqual(storage.current_game_version(self.c,'poe2'),'1.0')
  self.assertTrue(storage.has_consent(self.c,123,456,'2026-11-12-v2'))
  storage.initialize(self.c)
  self.assertEqual(settings.snapshot(self.c,DEFAULTS)['scan_interval_hours'],6)

 def test_failed_edit_is_atomic(self):
  original=settings.snapshot(self.c,DEFAULTS)
  with self.assertRaises(ValueError):settings.update_setting(self.c,DEFAULTS,'scan_interval_hours','100')
  self.assertEqual(original,settings.snapshot(self.c,DEFAULTS))

 def test_legacy_invalid_storage_falls_back_safely(self):
  storage.set_setting(self.c,'runtime:scan_interval_hours','999')
  self.assertEqual(settings.snapshot(self.c,DEFAULTS)['scan_interval_hours'],2)

 def test_english_translations(self):
  self.assertEqual(localization.translate('Brak zapisanych buildów.','en'),'No saved builds.')
  self.assertEqual(localization.translate('Brak zapisanych buildów.','pl'),'Brak zapisanych buildów.')
  self.assertIn('YouTube creator',localization.translate('Twórca na YouTube','en'))
  self.assertIn('Scan complete',localization.translate('Skan zakończony. Nowe filmy: **3**.','en'))

 def test_settings_have_bilingual_labels(self):
  self.assertGreaterEqual(len(settings.SETTINGS),12)
  for item in settings.SETTINGS:
   self.assertTrue(item.label_en and item.label_pl)
   self.assertTrue(item.description_en and item.description_pl)

 def test_ui_security_and_runtime_hooks_present(self):
  source=(Path(__file__).resolve().parents[1]/'main.py').read_text(encoding='utf-8')
  tree=ast.parse(source)
  classes={x.name for x in tree.body if isinstance(x,ast.ClassDef)}
  self.assertTrue({'SettingsModal','SettingsView','SettingsSelect','LanguageSelect','LanguageView'}<=classes)
  self.assertIn('interaction.user.id!=owner_id',source)
  self.assertIn('manage_guild',source)
  self.assertIn('storage.has_consent(c,guild_id,owner_id,POLICY_VERSION)',source)
  self.assertIn('automatic_scan.change_interval(hours=INTERVAL_H)',source)
  self.assertIn('automatic_link_refresh.change_interval(hours=LINK_REFRESH_INTERVAL_HOURS)',source)
  self.assertIn('automatic_version_check.change_interval(hours=VERSION_CHECK_INTERVAL_HOURS)',source)
  self.assertIn('runtime_settings.set_language(c,self.values[0])',source)
  self.assertIn('runtime_settings.update_setting(c,SETTING_DEFAULTS',source)

if __name__=='__main__':unittest.main()
