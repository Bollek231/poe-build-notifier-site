"""Community features for PoE Build Notifier v0.6.2.

Only bounded settings, bookmarks, temporary video IDs and short-lived statistics
are persisted. All input is validated without discord.py dependencies.
"""
from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo('Europe/Warsaw')
VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')
CLOCK = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d$')


def now_utc():
    return datetime.now(timezone.utc)


def init(connection):
    connection.execute('CREATE TABLE IF NOT EXISTS saved_builds (user_id TEXT NOT NULL, video_id TEXT NOT NULL, saved_at TEXT NOT NULL, PRIMARY KEY(user_id,video_id))')
    connection.execute('CREATE TABLE IF NOT EXISTS quiet_queue (video_id TEXT PRIMARY KEY, game TEXT NOT NULL, league TEXT NOT NULL, title TEXT NOT NULL, published_at TEXT NOT NULL, queued_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS video_trends (video_id TEXT NOT NULL, observed_at TEXT NOT NULL, view_count INTEGER NOT NULL, PRIMARY KEY(video_id,observed_at))')
    connection.execute('CREATE TABLE IF NOT EXISTS title_translations (source_hash TEXT PRIMARY KEY, english TEXT NOT NULL, cached_at TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS translation_usage (id INTEGER PRIMARY KEY AUTOINCREMENT, attempted_at TEXT NOT NULL)')
    connection.commit()


def cleanup(connection, days=7, now=None):
    cutoff=((now or now_utc())-timedelta(days=days)).isoformat()
    connection.execute('DELETE FROM quiet_queue WHERE queued_at < ?', (cutoff,))
    connection.execute('DELETE FROM video_trends WHERE observed_at < ?', (cutoff,))
    connection.execute('DELETE FROM title_translations WHERE cached_at < ?', (cutoff,))
    connection.execute('DELETE FROM translation_usage WHERE attempted_at < ?', (cutoff,))
    connection.commit()


def validate_quiet(start, end):
    if not CLOCK.fullmatch(start or '') or not CLOCK.fullmatch(end or '') or start==end:
        raise ValueError('Use two distinct times in HH:MM format, e.g. 23:00 08:00')
    return start,end


def is_quiet(now, start, end):
    if not start or not end:return False
    validate_quiet(start,end)
    local=now.astimezone(WARSAW).strftime('%H:%M')
    return start<=local<end if start<end else local>=start or local<end


def get_quiet(connection):
    from storage import get_setting
    return get_setting(connection,'quiet_start',''),get_setting(connection,'quiet_end','')


def set_quiet(connection, start='', end=''):
    from storage import set_setting
    if start or end:validate_quiet(start,end)
    set_setting(connection,'quiet_start',start)
    set_setting(connection,'quiet_end',end)


def pause_until(connection,now=None):
    from storage import get_setting
    raw=get_setting(connection,'pause_until','')
    if raw=='forever':return 'forever'
    try:dt=datetime.fromisoformat(raw)
    except ValueError:return None
    if dt.tzinfo is None:return None
    return dt if dt>(now or now_utc()) else None


def set_pause(connection, raw, now=None):
    from storage import set_setting
    value=(raw or '').strip().lower()
    if value=='forever':result='forever'
    else:
        match=re.fullmatch(r'(1|2|3|6|12|24)h',value)
        if not match:raise ValueError('Use 1h, 2h, 3h, 6h, 12h, 24h or forever')
        result=((now or now_utc())+timedelta(hours=int(match.group(1)))).isoformat()
    set_setting(connection,'pause_until',result)
    return result


def clear_pause(connection):
    from storage import set_setting
    set_setting(connection,'pause_until','')


def saved_toggle(connection, user_id, video_id, now=None):
    if not VIDEO_ID.fullmatch(video_id):raise ValueError('Invalid YouTube ID')
    user_id=str(user_id)
    existing=connection.execute('SELECT 1 FROM saved_builds WHERE user_id=? AND video_id=?',(user_id,video_id)).fetchone()
    if existing:
        connection.execute('DELETE FROM saved_builds WHERE user_id=? AND video_id=?',(user_id,video_id))
        state=False
    else:
        count=connection.execute('SELECT COUNT(*) FROM saved_builds WHERE user_id=?',(user_id,)).fetchone()[0]
        if count>=100:raise ValueError('Maximum 100 saved builds. Remove some first.')
        connection.execute('INSERT INTO saved_builds VALUES(?,?,?)',(user_id,video_id,(now or now_utc()).isoformat()))
        state=True
    connection.commit()
    return state


def saved_list(connection,user_id,limit=15):
    return [row[0] for row in connection.execute('SELECT video_id FROM saved_builds WHERE user_id=? ORDER BY saved_at DESC LIMIT ?', (str(user_id),limit))]


def saved_remove(connection,user_id,video_id=None):
    if video_id is not None and not VIDEO_ID.fullmatch(video_id):raise ValueError('Invalid YouTube ID')
    if video_id is None:cur=connection.execute('DELETE FROM saved_builds WHERE user_id=?',(str(user_id),))
    else:cur=connection.execute('DELETE FROM saved_builds WHERE user_id=? AND video_id=?',(str(user_id),video_id))
    connection.commit()
    return cur.rowcount


def queue_video(connection,video_id,game,league,title,published,now=None):
    if not VIDEO_ID.fullmatch(video_id):return False
    cur=connection.execute('INSERT OR IGNORE INTO quiet_queue VALUES(?,?,?,?,?,?)',(
        video_id,game,league,title[:240],published,(now or now_utc()).isoformat()))
    connection.commit()
    return cur.rowcount>0


def queued(connection,limit=25):
    return connection.execute('SELECT * FROM quiet_queue ORDER BY queued_at ASC LIMIT ?', (limit,)).fetchall()


def finish_queue(connection,rows,now=None):
    # Only after Discord successfully received the summary.
    stamp=(now or now_utc()).isoformat()
    for r in rows:
        vid=r['video_id'];url='https://www.youtube.com/watch?v='+vid
        connection.execute('INSERT OR IGNORE INTO videos VALUES(?,?,?,?,?)',(vid,r['title'],url,r['published_at'],stamp))
        connection.execute('DELETE FROM quiet_queue WHERE video_id=?',(vid,))
    connection.commit()


def record_views(connection, counts, observed=None):
    stamp=(observed or now_utc()).isoformat()
    for vid, views in counts.items():
        if VIDEO_ID.fullmatch(vid) and isinstance(views,int) and views>=0:
            connection.execute('INSERT OR IGNORE INTO video_trends VALUES(?,?,?)',(vid,stamp,views))
    connection.commit()


def trend_rank(connection,latest_counts,observed=None):
    observed=observed or now_utc()
    scores=[]
    for vid,current in latest_counts.items():
        older=connection.execute('SELECT view_count,observed_at FROM video_trends WHERE video_id=? AND observed_at < ? ORDER BY observed_at DESC LIMIT 1',(vid,observed.isoformat())).fetchone()
        if older:
            elapsed=max((observed-datetime.fromisoformat(older[1])).total_seconds()/3600,1/60)
            growth=max(0,current-older[0]);rate=growth/elapsed
            scores.append((vid,rate,growth,current,True))
        else:scores.append((vid,0.0,0,current,False))
    return sorted(scores,key=lambda v:(v[4],v[1],v[3]),reverse=True)


def title_hash(title):
    return hashlib.sha256(title.encode('utf-8')).hexdigest()


async def translate_to_english(session,connection,title,api_key,*,enabled=False,max_daily=30,now=None):
    """Google Cloud Translation Basic v2. Fail open; no token in URL/logs.

    The only outgoing text is the video title. Users must opt in and configure
    their own API key/billing. Max 30 calls/day by default; cache expires in 7d.
    """
    if not enabled or not api_key or not title:return title
    now=now or now_utc();hash_=title_hash(title)
    cache=connection.execute('SELECT english FROM title_translations WHERE source_hash=? AND cached_at >= ?',(
        hash_,(now-timedelta(days=7)).isoformat())).fetchone()
    if cache:return cache[0]
    since=(now-timedelta(days=1)).isoformat()
    used=connection.execute('SELECT COUNT(*) FROM translation_usage WHERE attempted_at >= ?',(since,)).fetchone()[0]
    if used>=max_daily:return title
    connection.execute('INSERT INTO translation_usage(attempted_at) VALUES(?)',(now.isoformat(),))
    connection.commit()
    try:
        import aiohttp
        async with session.post('https://translation.googleapis.com/language/translate/v2',
            json={'q':title[:450],'target':'en','format':'text'},
            headers={'X-Goog-Api-Key':api_key},timeout=aiohttp.ClientTimeout(total=8)) as response:
            if response.status!=200:return title
            result=await response.json(content_type=None)
        entries=result.get('data',{}).get('translations',[])
        if not entries:return title
        english=html.unescape(entries[0].get('translatedText','')).strip()
        if not english or len(english)>512:return title
        connection.execute('INSERT OR REPLACE INTO title_translations VALUES(?,?,?)',(hash_,english,now.isoformat()))
        connection.commit()
        return english
    except Exception:return title