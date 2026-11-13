"""Small, testable helpers for dynamic PoE leagues, daily digest and external links."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

POLAND = ZoneInfo('Europe/Warsaw')
VERSION_REGEX = re.compile(r'(?<!\d)3[.\-]\d{2}(?!\d)')
VALID_LEAGUE = re.compile(r'3\.\d{2}\Z')


def league_valid(value: str) -> bool:
    return bool(VALID_LEAGUE.fullmatch(value))


def normalize_league_match(value: str) -> str:
    return value.replace('-', '.')


def title_conflicts_with_league(title: str, league: str) -> bool:
    """An explicit old/different league in the VIDEO TITLE beats boilerplate descriptions."""
    return any(normalize_league_match(m.group()) != league for m in VERSION_REGEX.finditer(title))


def mentions_league(title: str, description: str, league: str) -> bool:
    return any(normalize_league_match(m.group()) == league for m in VERSION_REGEX.finditer(title + ' ' + description))


def rendered_queries(queries: list[str], league: str) -> list[str]:
    """Replace static 3.30 in old search_config.json without editing user settings."""
    result = []
    for q in queries:
        s = VERSION_REGEX.sub(league, q)
        if not VERSION_REGEX.search(s):
            s = s.rstrip() + ' ' + league
        result.append(s)
    return result


def digest_due(now: datetime, time_str: str, last_sent_date: str | None) -> bool:
    local = now.astimezone(POLAND)
    h, m = map(int, time_str.split(':'))
    return (local.hour, local.minute) >= (h, m) and last_sent_date != local.date().isoformat()


def digest_window(now: datetime) -> tuple[str, str]:
    """Rolling UTC 24-hour period, not calendar-day bounds: includes evening builds."""
    current = now.astimezone(timezone.utc)
    return (current - timedelta(hours=24)).isoformat(), current.isoformat()


def mobalytics_poe_url(raw: str) -> bool:
    """Never create a Mobalytics button for other games or lookalike hosts."""
    try:
        parsed = urlparse(raw)
        host = (parsed.hostname or '').lower()
        path = parsed.path.lower()
        return parsed.scheme in ('https', 'http') and host in ('mobalytics.gg','www.mobalytics.gg') and (path == '/poe' or path.startswith('/poe/'))
    except ValueError:
        return False
