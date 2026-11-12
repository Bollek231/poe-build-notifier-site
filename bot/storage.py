"""Minimal persistent storage and retention for PoE Build Notifier.

The schema retains compatibility with pre-audit poe330_seen.sqlite3 databases.
Only public YouTube metadata is subject to the short API cache lifetime; a
minimal Discord consent record is retained until revocation or policy change.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone, time
from zoneinfo import ZoneInfo
import sqlite3


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def initialize(connection: sqlite3.Connection) -> None:
    connection.execute('CREATE TABLE IF NOT EXISTS videos (video_id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, published_at TEXT, sent_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS builds (fingerprint TEXT PRIMARY KEY, canonical_title TEXT NOT NULL, first_video_id TEXT NOT NULL, created_at TEXT NOT NULL, league TEXT DEFAULT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS search_log (id INTEGER PRIMARY KEY AUTOINCREMENT, searched_at TEXT NOT NULL, query TEXT NOT NULL, kind TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS api_usage (id INTEGER PRIMARY KEY AUTOINCREMENT, used_at TEXT NOT NULL, units INTEGER NOT NULL, operation TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS video_metadata (video_id TEXT PRIMARY KEY, skill TEXT, ascendancy TEXT, classification TEXT)')
    connection.execute('CREATE TABLE IF NOT EXISTS discord_posts (message_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL, sent_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS privacy_consents (guild_id TEXT NOT NULL, user_id TEXT NOT NULL, policy_version TEXT NOT NULL, accepted_at TEXT NOT NULL, PRIMARY KEY (guild_id, user_id))')
    connection.execute('CREATE TABLE IF NOT EXISTS server_activation (guild_id TEXT PRIMARY KEY, policy_version TEXT NOT NULL, activated_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS quota_pauses (quota_type TEXT PRIMARY KEY, until_utc TEXT NOT NULL, notice_sent INTEGER NOT NULL DEFAULT 0)')
    connection.execute('CREATE TABLE IF NOT EXISTS bot_settings (name TEXT PRIMARY KEY, value TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS daily_digests (channel_id TEXT NOT NULL, digest_date TEXT NOT NULL, sent_at TEXT NOT NULL, PRIMARY KEY(channel_id, digest_date))')
    # Compatible with databases created by the old bot without a league column.
    columns = [row[1] for row in connection.execute('PRAGMA table_info(builds)').fetchall()]
    if 'league' not in columns:
        connection.execute('ALTER TABLE builds ADD COLUMN league TEXT DEFAULT NULL')
    connection.execute('UPDATE builds SET league=? WHERE league IS NULL', ('3.30',))
    connection.commit()


def cleanup(connection: sqlite3.Connection, retention_days: int = 7, *, now: datetime | None = None) -> dict[str, int]:
    """Delete cached YouTube API data older than a policy-safe retention window.

    Uses the existing timestamp columns (UTC ISO 8601) and removes dependent
    metadata rows after deleting cached video IDs. Does not delete active user
    consent records. The 7-day default stays well below the 30-day ceiling.
    """
    if not 1 <= retention_days <= 29:
        raise ValueError('retention_days must be between 1 and 29')
    current = now or utc_now()
    cutoff = (current - timedelta(days=retention_days)).isoformat()
    changes = {}
    for table, column in [
        ('videos', 'sent_at'), ('builds', 'created_at'),
        ('search_log', 'searched_at'), ('api_usage', 'used_at'),
    ]:
        cur = connection.execute(f'DELETE FROM {table} WHERE {column} < ?', (cutoff,))
        changes[table] = cur.rowcount
    # old legacy rows may have metadata without a valid current cached video.
    cur = connection.execute('DELETE FROM video_metadata WHERE video_id NOT IN (SELECT video_id FROM videos)')
    changes['video_metadata'] = cur.rowcount
    # Legacy bot revisions recorded Discord message IDs to delete them later.
    # Remove these stale tracking IDs from SQLite only; NEVER delete Discord posts.
    changes['discord_posts_tracking'] = connection.execute('DELETE FROM discord_posts').rowcount
    connection.commit()
    return changes


def has_consent(connection: sqlite3.Connection, guild_id: int, user_id: int, version: str) -> bool:
    return connection.execute('SELECT 1 FROM privacy_consents WHERE guild_id=? AND user_id=? AND policy_version=?', (str(guild_id), str(user_id), version)).fetchone() is not None


def record_consent(connection: sqlite3.Connection, guild_id: int, user_id: int, version: str) -> None:
    connection.execute('INSERT OR REPLACE INTO privacy_consents (guild_id,user_id,policy_version,accepted_at) VALUES (?,?,?,?)', (str(guild_id), str(user_id), version, utc_now().isoformat()))
    connection.commit()


def revoke_consent(connection: sqlite3.Connection, guild_id: int, user_id: int) -> None:
    connection.execute('DELETE FROM privacy_consents WHERE guild_id=? AND user_id=?', (str(guild_id), str(user_id)))
    connection.commit()


# YouTube API quota windows start at midnight Pacific Time (not Warsaw time).
def next_search_quota_reset(*, now: datetime | None = None) -> datetime:
    from datetime import date
    current = (now or utc_now()).astimezone(ZoneInfo('America/Los_Angeles'))
    next_day = current.date() + timedelta(days=1)
    return datetime.combine(next_day, time.min, tzinfo=ZoneInfo('America/Los_Angeles')).astimezone(timezone.utc)


def is_daily_search_quota_error(status: int, payload: object) -> bool:
    if status not in (403, 429):
        return False
    message = str(payload).casefold()
    # Separate daily Search Queries exhaustion from other 403/429 causes.
    return ('search queries per day' in message and 'quota' in message) or ('dailylimitexceeded' in message and 'search' in message)


def quota_pause(connection: sqlite3.Connection, *, now: datetime | None = None) -> tuple[datetime, bool] | None:
    row = connection.execute("SELECT until_utc, notice_sent FROM quota_pauses WHERE quota_type='search.list'").fetchone()
    if row is None:
        return None
    try:
        until = datetime.fromisoformat(row[0]).astimezone(timezone.utc)
    except (TypeError, ValueError):
        until = utc_now() - timedelta(seconds=1)
    if until <= (now or utc_now()):
        connection.execute("DELETE FROM quota_pauses WHERE quota_type='search.list'")
        connection.commit()
        return None
    return until, bool(row[1])


def begin_quota_pause(connection: sqlite3.Connection, reset_at: datetime) -> None:
    # Persist this state so restarting the bot doesn't trigger another burst
    # of API calls or repeated Discord alerts.
    connection.execute(
        "INSERT OR REPLACE INTO quota_pauses(quota_type,until_utc,notice_sent) VALUES('search.list',?,0)",
        (reset_at.astimezone(timezone.utc).isoformat(),)
    )
    connection.commit()


def mark_quota_notice_sent(connection: sqlite3.Connection) -> None:
    connection.execute("UPDATE quota_pauses SET notice_sent=1 WHERE quota_type='search.list'")
    connection.commit()


def get_setting(connection: sqlite3.Connection, name: str, default: str) -> str:
    row = connection.execute('SELECT value FROM bot_settings WHERE name=?', (name,)).fetchone()
    return row[0] if row else default


def set_setting(connection: sqlite3.Connection, name: str, value: str) -> None:
    connection.execute('INSERT INTO bot_settings(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value', (name,value))
    connection.commit()


def current_league(connection: sqlite3.Connection, default: str='3.30') -> str:
    return get_setting(connection, 'target_league', default)


def set_league(connection: sqlite3.Connection, league: str) -> None:
    from features import league_valid
    if not league_valid(league):
        raise ValueError('League version must use 3.xx (for example 3.31)')
    set_setting(connection, 'target_league', league)


def digest_sent_date(connection: sqlite3.Connection, channel_id: int, day: str) -> bool:
    return connection.execute('SELECT 1 FROM daily_digests WHERE channel_id=? AND digest_date=?', (str(channel_id),day)).fetchone() is not None


def mark_digest_sent(connection: sqlite3.Connection, channel_id: int, day: str, *, sent_at: datetime | None = None) -> None:
    stamp=(sent_at or utc_now()).astimezone(timezone.utc).isoformat()
    connection.execute('INSERT OR IGNORE INTO daily_digests(channel_id,digest_date,sent_at) VALUES(?,?,?)', (str(channel_id),day,stamp))
    connection.commit()


def digest_builds(connection: sqlite3.Connection, league: str, start: str, end: str, limit: int = 40):
    """Only posted builds; search-result duplicates are not builds. No API calls."""
    return connection.execute("""
        SELECT b.canonical_title, b.first_video_id, b.created_at, m.skill, m.ascendancy, m.classification
        FROM builds b
        JOIN videos v ON v.video_id=b.first_video_id
        LEFT JOIN video_metadata m ON m.video_id=v.video_id
        WHERE b.league=? AND b.created_at>=? AND b.created_at<=?
        ORDER BY b.created_at DESC LIMIT ?
    """, (league, start, end, limit)).fetchall()