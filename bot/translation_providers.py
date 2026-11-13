"""Optional English title translation with selectable Google and MyMemory backends.

Only accepted public video titles leave the bot. Errors always return the
original title; both providers have local request caps and seven-day caches.
"""
from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timedelta, timezone

PROVIDERS = ('mymemory', 'google')
CONTACT_EMAIL = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def normalize_provider(raw):
    value = str(raw or '').strip().lower()
    if value not in PROVIDERS:
        raise ValueError('Choose mymemory or google')
    return value


def init(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS translation_cache_v2 (
        provider TEXT NOT NULL, source_hash TEXT NOT NULL, english TEXT NOT NULL,
        cached_at TEXT NOT NULL, PRIMARY KEY(provider, source_hash))''')
    connection.execute('''CREATE TABLE IF NOT EXISTS translation_requests_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT, provider TEXT NOT NULL,
        attempted_at TEXT NOT NULL, source_chars INTEGER NOT NULL)''')
    connection.commit()


def cleanup(connection, retention_days=7, *, now=None):
    now = now or datetime.now(timezone.utc)
    cache_limit = (now-timedelta(days=retention_days)).isoformat()
    request_limit = (now-timedelta(days=2)).isoformat()
    connection.execute('DELETE FROM translation_cache_v2 WHERE cached_at < ?', (cache_limit,))
    connection.execute('DELETE FROM translation_requests_v2 WHERE attempted_at < ?', (request_limit,))
    connection.commit()


def detect_source(title, preferred=None):
    """MyMemory requires a language pair; detect text locally if possible.

    Fall back to YouTube's language tag only if detection is not confident.
    Unknown languages are not guessed or silently sent as English.
    """
    try:
        from langdetect import DetectorFactory, detect_langs
        DetectorFactory.seed = 0
        guesses = detect_langs(title)
        if guesses and guesses[0].prob >= .65:
            lang = guesses[0].lang.lower()
            if re.fullmatch(r'[a-z]{2,3}(?:-[a-z]{2,4})?', lang):
                return lang
    except Exception:
        # Translation must not fail if the detector cannot parse a title.
        pass
    lang = str(preferred or '').lower().split(',')[0].split('-')[0].strip()
    return lang if re.fullmatch(r'[a-z]{2,3}', lang) else None


def daily_usage(connection, provider, since):
    row = connection.execute('''SELECT COUNT(*),COALESCE(SUM(source_chars),0)
        FROM translation_requests_v2 WHERE provider=? AND attempted_at >= ?''',
        (provider, since)).fetchone()
    return row[0], row[1]


async def translate_to_english(session, connection, title, *, provider='mymemory',
                               google_api_key='', contact_email='', enabled=False,
                               max_daily=30, source_language=None, now=None):
    if not enabled or not title or not isinstance(title, str):
        return title
    try:provider = normalize_provider(provider)
    except ValueError:return title
    if provider == 'google' and not google_api_key:return title
    if not 1 <= max_daily <= 100:return title
    now = now or datetime.now(timezone.utc)
    h = hashlib.sha256(title.encode('utf-8')).hexdigest()
    cutoff = (now-timedelta(days=7)).isoformat()
    cached = connection.execute('''SELECT english FROM translation_cache_v2
        WHERE provider=? AND source_hash=? AND cached_at>=?''', (provider,h,cutoff)).fetchone()
    if cached:return cached[0]
    if provider == 'google':
        # v0.6.2 cache: don't lose translations during the upgrade.
        try:
            legacy = connection.execute('''SELECT english FROM title_translations
                WHERE source_hash=? AND cached_at>=?''',(h,cutoff)).fetchone()
            if legacy:return legacy[0]
        except Exception:pass

    lang = detect_source(title, source_language)
    if lang == 'en':return title
    if provider == 'mymemory' and not lang:return title
    size = len(title.encode('utf-8'))
    if provider == 'mymemory' and size > 500:return title  # provider hard cap
    # Protect service and data: our requests never contain descriptions or tokens.
    since = (now-timedelta(days=1)).isoformat()
    attempts, chars = daily_usage(connection,provider,since)
    if provider == 'google':
        # Keep the previous Google usage cap when upgrading from v0.6.2.
        try:
            attempts += connection.execute('''SELECT COUNT(*) FROM translation_usage
                WHERE attempted_at >= ?''',(since,)).fetchone()[0]
        except Exception:pass
    else:
        # MyMemory offers 5000 characters/day without email, 50000 with email.
        # Keep a small margin for external/shared usage and rolling-window resets.
        email = contact_email.strip() if CONTACT_EMAIL.fullmatch(contact_email.strip()) else ''
        budget = 45000 if email else 4500
        if chars + len(title) > budget:return title
    if attempts >= max_daily:return title
    connection.execute('''INSERT INTO translation_requests_v2(provider,attempted_at,source_chars)
        VALUES(?,?,?)''',(provider,now.isoformat(),len(title)))
    connection.commit()
    try:
        import aiohttp
        if provider == 'google':
            async with session.post('https://translation.googleapis.com/language/translate/v2',
                 json={'q':title[:450],'target':'en','format':'text'},
                 headers={'X-Goog-Api-Key':google_api_key},
                 timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status != 200:return title
                payload = await response.json(content_type=None)
            options = payload.get('data',{}).get('translations',[])
            translated = options[0].get('translatedText','') if options else ''
        else:
            params={'q':title,'langpair':lang+'|en','mt':'1'}
            if email:params['de']=email
            async with session.get('https://api.mymemory.translated.net/get',
                 params=params,timeout=aiohttp.ClientTimeout(total=9)) as response:
                if response.status != 200:return title
                payload = await response.json(content_type=None)
            if int(payload.get('responseStatus',0)) != 200:return title
            translated = payload.get('responseData',{}).get('translatedText','')
        english = html.unescape(translated).strip() if isinstance(translated,str) else ''
        if not english or len(english)>512 or 'MYMEMORY WARNING' in english.upper():return title
        connection.execute('''INSERT OR REPLACE INTO translation_cache_v2
            (provider,source_hash,english,cached_at) VALUES(?,?,?,?)''',
            (provider,h,english,now.isoformat()))
        connection.commit()
        return english
    except Exception:
        return title
