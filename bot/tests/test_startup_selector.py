"""Startup button selector v0.6.5: no automatic scans until an admin opts in."""
import sqlite3
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
import main
import storage


class KeepOpen:
    def __init__(self, connection):
        self.connection = connection

    def close(self):
        pass

    def __getattr__(self, key):
        return getattr(self.connection, key)


class StartupSelectorTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.old_choice = main.bot._startup_choice
        main.bot._startup_choice = None

    def tearDown(self):
        main.bot._startup_choice = self.old_choice

    def database(self):
        c = sqlite3.connect(":memory:")
        storage.initialize(c)
        return c

    def interaction(self, *, admin=True, channel=None):
        item = Mock()
        item.guild = Mock(id=5678)
        item.channel_id = main.CHANNEL_ID if channel is None else channel
        item.user = Mock(id=1234)
        item.user.guild_permissions.manage_guild = admin
        item.response.send_message = AsyncMock()
        item.response.edit_message = AsyncMock()
        item.message.edit = AsyncMock()
        return item

    def test_ui_is_persistent_and_has_exactly_two_buttons(self):
        view = main.StartupScanView()
        self.assertIsNone(view.timeout)
        self.assertEqual([x.label for x in view.children], ["Buildy", "Farm Strat"])
        self.assertEqual([x.custom_id for x in view.children],
                         ["poe_startup_select_build", "poe_startup_select_farm"])
        disabled = main.StartupScanView(disabled=True)
        self.assertTrue(all(item.disabled for item in disabled.children))
        self.assertIn("Buildy", main.startup_panel_embed().description)
        self.assertIn("Farm Strat", main.startup_panel_embed().description)

    async def test_all_auto_scans_are_gated_before_selection(self):
        # In particular do not even open SQLite or spend any API quota.
        with patch.object(main, "db") as db:
            result = await main.scan('auto')
            self.assertEqual(result['searched'], 0)
            db.assert_not_called()
        with patch.object(main, "scan", new_callable=AsyncMock) as fake_scan:
            await main.automatic_scan.coro()
            await main.automatic_digest.coro()
            await main.automatic_quiet_flush.coro()
            fake_scan.assert_not_awaited()

    async def test_selected_build_only_runs_build_scheduled_scans(self):
        main.bot._startup_choice = 'build'
        with patch.object(main, "scan", new_callable=AsyncMock) as fake_scan, \
             patch.object(main, "db") as db:
            await main.automatic_scan.coro()
            fake_scan.assert_awaited_once_with('auto',content_type='build')
            db.assert_not_called()

    async def test_selected_farming_respects_farm_auto_setting(self):
        main.bot._startup_choice = 'farm'
        with patch.object(main, "scan", new_callable=AsyncMock) as fake_scan, \
             patch.object(main, "db", return_value=Mock()), \
             patch.object(main.storage, "get_setting", return_value='false'):
            await main.automatic_scan.coro()
            fake_scan.assert_not_awaited()
        with patch.object(main, "scan", new_callable=AsyncMock) as fake_scan, \
             patch.object(main, "db", return_value=Mock()), \
             patch.object(main.storage, "get_setting", return_value='true'):
            await main.automatic_scan.coro()
            fake_scan.assert_awaited_once_with('auto',content_type='farm')

    async def test_unauthorized_user_cannot_choose(self):
        view = main.StartupScanView()
        actor = self.interaction(admin=False)
        with patch.object(main, "db") as db, \
             patch.object(main, "scan", new_callable=AsyncMock) as search:
            await view.select(actor, 'build')
            db.assert_not_called()
            search.assert_not_awaited()
        self.assertIsNone(main.bot._startup_choice)
        actor.response.send_message.assert_awaited_once()

    async def test_user_must_accept_policy_before_start(self):
        actor = self.interaction()
        c = self.database()
        try:
            with patch.object(main, "db", side_effect=lambda: KeepOpen(c)), \
                 patch.object(main, "scan", new_callable=AsyncMock) as search:
                await main.StartupScanView().select(actor, 'farm')
                search.assert_not_awaited()
            actor.response.send_message.assert_awaited_once()
            self.assertIsNone(main.bot._startup_choice)
        finally:
            c.close()

    async def test_one_click_scans_only_chosen_mode_and_disables_buttons(self):
        actor = self.interaction()
        c = self.database()
        storage.record_consent(c,actor.guild.id,actor.user.id,main.POLICY_VERSION)
        try:
            result={'sent':2,'queued':0,'searched':1,'warning':''}
            with patch.object(main, "db", side_effect=lambda: KeepOpen(c)), \
                 patch.object(main, "scan", new_callable=AsyncMock, return_value=result) as search:
                await main.StartupScanView().select(actor, 'farm')
                search.assert_awaited_once_with('manual',content_type='farm')
                await main.StartupScanView().select(actor, 'build')
                search.assert_awaited_once()
            self.assertEqual(main.bot._startup_choice, 'farm')
            actor.response.edit_message.assert_awaited_once()
            updated=actor.response.edit_message.await_args.kwargs
            self.assertTrue(all(x.disabled for x in updated['view'].children))
            self.assertIn('Farm Strat',updated['embed'].title)
            self.assertEqual(actor.message.edit.await_count, 1)
            self.assertIn('2',actor.message.edit.await_args.kwargs['embed'].description)
        finally:
            c.close()

    async def test_show_panel_reuses_message_after_restart(self):
        c = self.database()
        msg = Mock(id=123456)
        msg.edit = AsyncMock()
        channel = Mock()
        channel.send = AsyncMock(return_value=msg)
        channel.fetch_message = AsyncMock(return_value=msg)
        try:
            with patch.object(main, "db", side_effect=lambda: KeepOpen(c)), \
                 patch.object(main.bot, "get_channel", return_value=channel):
                await main.show_startup_panel()
                self.assertEqual(storage.get_setting(c,'startup_panel_message_id',''),str(msg.id))
                await main.show_startup_panel()
                channel.send.assert_awaited_once()
                channel.fetch_message.assert_awaited_once_with(msg.id)
                msg.edit.assert_awaited_once()
                self.assertTrue(all(not item.disabled for item in msg.edit.await_args.kwargs['view'].children))
        finally:
            c.close()


if __name__=="__main__":
    unittest.main()
