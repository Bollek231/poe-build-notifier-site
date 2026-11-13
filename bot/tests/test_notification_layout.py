"""Native Discord notification redesign regression tests for v0.6.4d."""
from datetime import datetime, timezone
import sqlite3
import unittest
from unittest.mock import AsyncMock, Mock, patch

import discord
import main
import storage


VIDEO_ID = "N12AbcDeFgH"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"
PUBLISHED = datetime(2026, 11, 13, 16, 32, tzinfo=timezone.utc)


class NotificationLayoutTests(unittest.TestCase):
    def create(self, *, farm=False, style="expanded", language="pl", translated=None):
        title = "Atlas currency farming guide" if farm else "Holy Relic of Conviction Starter"
        return main.notification_embed(
            title=title,
            translated=title if translated is None else translated,
            url=VIDEO_URL,
            game="poe1",
            league="3.30",
            category="Atlas / Mapping" if farm else "League Starter",
            channel_title="POEGUY" if farm else "kalibar",
            published=PUBLISHED,
            thumbnail="https://i.ytimg.com/vi/N12AbcDeFgH/hqdefault.jpg",
            content_type="farm" if farm else "build",
            skill="Holy Relic" if not farm else None,
            ascendancy=None,
            style=style,
            language=language,
        )

    def test_distinct_purple_and_gold_themes(self):
        build = self.create()
        farm = self.create(farm=True)
        self.assertNotEqual(build.color, farm.color)
        self.assertEqual(build.color, discord.Color.from_rgb(170, 93, 235))
        self.assertEqual(farm.color, discord.Color.from_rgb(237, 176, 49))
        self.assertIn("BUILD GUIDE", build.author.name)
        self.assertIn("FARMING STRATEGY", farm.author.name)

    def test_expanded_build_fields_are_clean_and_readable(self):
        embed = self.create()
        labels = [field.name for field in embed.fields]
        self.assertTrue(any("Umiejętność" in label for label in labels))
        self.assertTrue(any("Twórca" in label for label in labels))
        self.assertTrue(any("Liga" in label for label in labels))
        self.assertFalse(any("oznaczenie bota" in label for label in labels))
        self.assertTrue(any("Holy Relic" in field.value for field in embed.fields))
        self.assertEqual(embed.url, VIDEO_URL)
        self.assertEqual(embed.thumbnail.url, "https://i.ytimg.com/vi/N12AbcDeFgH/hqdefault.jpg")

    def test_compact_has_no_unnecessary_fields(self):
        build = self.create(style="compact")
        farm = self.create(farm=True, style="compact")
        self.assertEqual(len(build.fields), 0)
        self.assertEqual(len(farm.fields), 0)
        self.assertIn("League Starter", build.description)
        self.assertIn("Atlas / Mapping", farm.description)
        self.assertIn("POEGUY", farm.description)

    def test_english_and_original_titles(self):
        embed = self.create(language="en", translated="Translated video")
        self.assertEqual(embed.title, "Translated video")
        self.assertIn("Original title", embed.description)
        self.assertIn("Holy Relic of Conviction Starter", embed.description)
        self.assertTrue(any("Published" in field.name for field in embed.fields))

    def test_discord_limits_and_mentions(self):
        embed = main.notification_embed(
            title="@everyone" + "x"*3000, translated="@everyone" + "x"*3000,
            url=VIDEO_URL, game="poe2", league="1.0", category="Bossing",
            channel_title="@here" + "X"*2000, published=PUBLISHED,
            content_type="farm", style="expanded", language="en")
        self.assertLessEqual(len(embed.title), 256)
        self.assertLessEqual(len(embed.author.name), 256)
        self.assertLessEqual(len(embed.description), 4096)
        self.assertLessEqual(len(embed.fields), 25)
        self.assertTrue(all(len(f.name)<=256 and len(f.value)<=1024 for f in embed.fields))
        self.assertNotIn("@everyone", embed.title)
        self.assertNotIn("@here", "".join(f.value for f in embed.fields))

    def test_buttons_include_youtube_and_optional_guides(self):
        view = main.buttons_from_links({
            "Path of Building": "https://pobb.in/abc",
            "Maxroll": "https://maxroll.gg/poe/build-guides/abc",
            "Mobalytics": "https://mobalytics.gg/poe/builds/abc",
            "PoE Planner": "https://poeplanner.com/a/abc"
        }, VIDEO_ID)
        labels = [getattr(component, "label", None) or
                  getattr(getattr(component, "item", None), "label", None)
                  for component in view.children]
        for label in ("⭐ Save / Zapisz", "YouTube", "PoB", "Maxroll", "Mobalytics", "PoE Planner"):
            self.assertIn(label, labels)
        self.assertEqual(len(view.children), 6)
        self.assertTrue(any(b.url==VIDEO_URL for b in view.children if b.label=="YouTube"))

    def test_invalid_external_url_is_not_button(self):
        view = main.buttons_from_links({"PoE Planner":"https://poeplanner.com.evil.test/x"},VIDEO_ID)
        self.assertNotIn("PoE Planner",[
            getattr(component, "label", None) or
            getattr(getattr(component, "item", None), "label", None)
            for component in view.children])

    def test_style_is_persistable_in_existing_settings(self):
        c=sqlite3.connect(":memory:")
        try:
            storage.initialize(c)
            self.assertEqual(storage.get_setting(c,"embed_style","expanded"),"expanded")
            storage.set_setting(c,"embed_style","compact")
            self.assertEqual(storage.get_setting(c,"embed_style","expanded"),"compact")
        finally:
            c.close()


class EmbedStyleCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_style_does_not_write(self):
        ctx=Mock()
        with patch.object(main,"require_consent",new_callable=AsyncMock,return_value=True), \
             patch.object(main,"localized_reply",new_callable=AsyncMock) as reply, \
             patch.object(main,"db") as db:
            await main.embed_style_command.callback(ctx,"rainbow")
            db.assert_not_called()
            reply.assert_awaited_once()

    async def test_selected_style_is_written_and_can_be_read(self):
        ctx=Mock()
        c=sqlite3.connect(":memory:")
        storage.initialize(c)
        class NoClose:
            def __init__(self, connection):self.c=connection
            def __getattr__(self,name):return getattr(self.c,name)
            def close(self):pass
        try:
            with patch.object(main,"require_consent",new_callable=AsyncMock,return_value=True), \
                 patch.object(main,"localized_reply",new_callable=AsyncMock) as reply, \
                 patch.object(main,"db",side_effect=lambda:NoClose(c)):
                await main.embed_style_command.callback(ctx,"compact")
                self.assertEqual(storage.get_setting(c,"embed_style","expanded"),"compact")
                await main.embed_style_command.callback(ctx,"status")
                self.assertEqual(reply.await_count,2)
        finally:
            c.close()


if __name__ == "__main__":
    unittest.main()
