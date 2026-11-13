"""Regression tests for optional per-scan video caps (v0.6.4b)."""
import unittest
from unittest.mock import AsyncMock, Mock, patch

import enhancements
import main


class ScanLimitValidationTests(unittest.TestCase):
    def test_optional_limit(self):
        self.assertIsNone(enhancements.parse_scan_limit(""))
        self.assertIsNone(enhancements.parse_scan_limit("  "))
        for number in (1, 2, 10, 25):
            self.assertEqual(enhancements.parse_scan_limit(str(number)), number)

    def test_invalid_limit(self):
        for bad in ("0", "-1", "26", "999", "1.5", "1,2", "2abc", "1 2", "+1", "01"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                enhancements.parse_scan_limit(bad)

    def test_limit_stops_exactly_at_requested_count(self):
        self.assertFalse(enhancements.scan_limit_reached(0, 1))
        self.assertTrue(enhancements.scan_limit_reached(1, 1))
        self.assertFalse(enhancements.scan_limit_reached(1, 2))
        self.assertTrue(enhancements.scan_limit_reached(2, 2))
        self.assertFalse(enhancements.scan_limit_reached(100, None))


class ScanCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_scan_without_number_retains_full_scan(self):
        ctx = Mock()
        with patch.object(main, "require_consent", new_callable=AsyncMock, return_value=True), \
             patch.object(main, "report_scan", new_callable=AsyncMock) as report:
            await main.scan_command.callback(ctx)
            report.assert_awaited_once_with(ctx, max_videos=None)

    async def test_scan_one_or_two(self):
        for text, count in (("1", 1), ("2", 2), ("25", 25)):
            with self.subTest(count=count):
                ctx = Mock()
                with patch.object(main, "require_consent", new_callable=AsyncMock, return_value=True), \
                     patch.object(main, "report_scan", new_callable=AsyncMock) as report:
                    await main.scan_command.callback(ctx, text)
                    report.assert_awaited_once_with(ctx, max_videos=count)

    async def test_farm_scan_without_count(self):
        ctx = Mock()
        with patch.object(main, "require_consent", new_callable=AsyncMock, return_value=True), \
             patch.object(main, "report_scan", new_callable=AsyncMock) as report:
            await main.farm_scan_command.callback(ctx)
            report.assert_awaited_once_with(ctx, content_type="farm", max_videos=None)

    async def test_farm_scan_limited(self):
        ctx = Mock()
        with patch.object(main, "require_consent", new_callable=AsyncMock, return_value=True), \
             patch.object(main, "report_scan", new_callable=AsyncMock) as report:
            await main.farm_scan_command.callback(ctx, "2")
            report.assert_awaited_once_with(ctx, content_type="farm", max_videos=2)

    async def test_invalid_scan_count_does_not_run_scan(self):
        for command in (main.scan_command, main.farm_scan_command):
            ctx = Mock()
            with patch.object(main, "require_consent", new_callable=AsyncMock, return_value=True), \
                 patch.object(main, "localized_reply", new_callable=AsyncMock) as reply, \
                 patch.object(main, "report_scan", new_callable=AsyncMock) as report:
                await command.callback(ctx, "nope")
                report.assert_not_awaited()
                reply.assert_awaited_once()

    async def test_consent_still_required(self):
        ctx = Mock()
        with patch.object(main, "require_consent", new_callable=AsyncMock, return_value=False), \
             patch.object(main, "report_scan", new_callable=AsyncMock) as report:
            await main.farm_scan_command.callback(ctx, "1")
            report.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
