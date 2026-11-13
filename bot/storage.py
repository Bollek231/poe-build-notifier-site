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
    # v0.5.1: additive migration. No existing data or Discord messages are removed.
    connection.execute('CREATE TABLE IF NOT EXISTS channel_rules (channel_id TEXT PRIMARY KEY, rule TEXT NOT NULL CHECK(rule IN (\'allow\',\'block\')), updated_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS posted_messages (video_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL, message_id TEXT NOT NULL, links_json TEXT NOT NULL, checked_at TEXT NOT NULL, created_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS link_checks (url TEXT PRIMARY KEY, state TEXT NOT NULL, checked_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS alert_events (name TEXT PRIMARY KEY, notified_at TEXT NOT NULL)')
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
    # Only refresh links for recently published posts; never delete their Discord messages.
    changes['posted_messages'] = connection.execute('DELETE FROM posted_messages WHERE created_at < ?', (cutoff,)).rowcount
    changes['link_checks'] = connection.execute('DELETE FROM link_checks WHERE checked_at < ?', (cutoff,)).rowcount
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


def current_game(connection: sqlite3.Connection) -> str:
    """Persistent game selection, defaulting to legacy PoE 1 installations."""
    from game_modes import normalize_game
    return normalize_game(get_setting(connection,'target_game','poe1')) or 'poe1'


def set_game(connection: sqlite3.Connection, game: str) -> None:
    from game_modes import normalize_game
    normalized=normalize_game(game)
    if normalized is None:raise ValueError('Game must be poe1 or poe2')
    set_setting(connection,'target_game',normalized)


def current_game_version(connection: sqlite3.Connection, game: str, *,
                         poe1_default: str='3.30', poe2_default: str='1.0') -> str:
    """Keep separate league/patch settings; never overwrite a user's PoE 1 league."""
    if game=='poe2':return get_setting(connection,'target_version_poe2',poe2_default)
    if game=='poe1':return current_league(connection,poe1_default)
    raise ValueError('Unsupported game')


def set_game_version(connection: sqlite3.Connection, game: str, version: str) -> None:
    if game=='poe1':
        set_league(connection,version)
    elif game=='poe2':
        from game_modes import valid_poe2_version
        if not valid_poe2_version(version):raise ValueError('PoE 2 version must use X.Y, e.g. 1.0')
        set_setting(connection,'target_version_poe2',version)
    else:raise ValueError('Unsupported game')


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


# v0.5.1: channel rules and filters survive the 7-day YouTube cache cleanup.
def put_channel_rule(connection: sqlite3.Connection, channel_id: str, rule: str) -> None:
    if rule not in ('allow','block'):
        raise ValueError('rule must be allow or block')
    from enhancements import youtube_channel_id
    if youtube_channel_id(channel_id) != channel_id:
        raise ValueError('Invalid YouTube channel ID')
    connection.execute('INSERT INTO channel_rules(channel_id,rule,updated_at) VALUES(?,?,?) '
                       'ON CONFLICT(channel_id) DO UPDATE SET rule=excluded.rule,updated_at=excluded.updated_at',
                       (channel_id,rule,utc_now().isoformat()))
    connection.commit()


def delete_channel_rule(connection: sqlite3.Connection, channel_id: str) -> bool:
    result=connection.execute('DELETE FROM channel_rules WHERE channel_id=?',(channel_id,))
    connection.commit()
    return result.rowcount>0


def channel_rule(connection: sqlite3.Connection, channel_id: str) -> str | None:
    row=connection.execute('SELECT rule FROM channel_rules WHERE channel_id=?',(channel_id,)).fetchone()
    return row[0] if row else None


def all_channel_rules(connection: sqlite3.Connection):
    return connection.execute('SELECT channel_id,rule FROM channel_rules ORDER BY rule,channel_id').fetchall()


def get_filters(connection: sqlite3.Connection, game: str='poe1') -> dict:
    import json
    from enhancements import normalize_filters
    try:return normalize_filters(json.loads(get_setting(connection,'build_filters' if game=='poe1' else 'build_filters_poe2','{}')))
    except (TypeError,ValueError):return {}


def set_filters(connection: sqlite3.Connection, filters: dict, game: str='poe1') -> None:
    import json
    from enhancements import normalize_filters
    set_setting(connection,'build_filters' if game=='poe1' else 'build_filters_poe2',json.dumps(normalize_filters(filters),ensure_ascii=False,sort_keys=True))


def record_post(connection: sqlite3.Connection, video_id: str, channel_id: int, message_id: int,
                links: dict, *, now: datetime | None=None) -> None:
    import json
    stamp=(now or utc_now()).astimezone(timezone.utc).isoformat()
    connection.execute('INSERT OR REPLACE INTO posted_messages(video_id,channel_id,message_id,links_json,checked_at,created_at) VALUES(?,?,?,?,?,?)',
                       (video_id,str(channel_id),str(message_id),json.dumps(links,sort_keys=True),stamp,stamp))
    connection.commit()


def refresh_candidates(connection: sqlite3.Connection, *, cutoff: datetime, limit: int=10):
    return connection.execute('SELECT video_id,channel_id,message_id,links_json,checked_at FROM posted_messages '
       'WHERE checked_at <= ? ORDER BY checked_at ASC LIMIT ?', (cutoff.astimezone(timezone.utc).isoformat(),limit)).fetchall()


def update_post_links(connection: sqlite3.Connection, video_id: str, links: dict | None) -> None:
    import json
    stamp=utc_now().isoformat()
    if links is None:
        connection.execute('UPDATE posted_messages SET checked_at=? WHERE video_id=?',(stamp,video_id))
    else:
        connection.execute('UPDATE posted_messages SET links_json=?,checked_at=? WHERE video_id=?',
                           (json.dumps(links,sort_keys=True),stamp,video_id))
    connection.commit()


def remove_post_tracking(connection: sqlite3.Connection, video_id: str) -> None:
    connection.execute('DELETE FROM posted_messages WHERE video_id=?',(video_id,))
    connection.commit()


def cached_link_state(connection: sqlite3.Connection, url: str, *, max_age_hours: int=12) -> str | None:
    row=connection.execute('SELECT state,checked_at FROM link_checks WHERE url=?',(url,)).fetchone()
    if not row:return None
    try:time_of_check=datetime.fromisoformat(row[1])
    except ValueError:return None
    if (utc_now()-time_of_check)>timedelta(hours=max_age_hours):return None
    return row[0]


def store_link_state(connection: sqlite3.Connection, url: str, state: str) -> None:
    if state not in ('ok','dead','uncertain'):raise ValueError('Invalid link state')
    connection.execute('INSERT OR REPLACE INTO link_checks(url,state,checked_at) VALUES(?,?,?)',
                       (url,state,utc_now().isoformat()))
    connection.commit()


def alert_allowed(connection: sqlite3.Connection, key: str, *, cooldown_minutes: int=60,now: datetime | None=None) -> bool:
    current=now or utc_now()
    row=connection.execute('SELECT notified_at FROM alert_events WHERE name=?',(key,)).fetchone()
    if not row:return True
    try:return current-datetime.fromisoformat(row[0])>=timedelta(minutes=cooldown_minutes)
    except (TypeError,ValueError):return True


def record_alert(connection: sqlite3.Connection,key: str, *, now: datetime | None=None) -> None:
    connection.execute('INSERT OR REPLACE INTO alert_events(name,notified_at) VALUES(?,?)',(key,(now or utc_now()).isoformat()))
    connection.commit()
