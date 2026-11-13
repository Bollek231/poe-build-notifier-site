import asyncio
import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse, parse_qs
from difflib import SequenceMatcher
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import storage
import features
import enhancements
import services
import backups
import game_modes

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('poe330')
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()
API_KEY = os.getenv('YOUTUBE_API_KEY', '').strip()
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))
DB_PATH = os.getenv('DB_PATH', 'poe330_seen.sqlite3')
INTERVAL_H = max(1, int(os.getenv('CHECK_INTERVAL_HOURS', '2')))
MAX_RESULTS = min(50, max(1, int(os.getenv('MAX_RESULTS_PER_QUERY', '25'))))
SEND_DELAY = max(0, float(os.getenv('SEND_DELAY_SECONDS', '3')))
MAX_VIDEO_AGE_HOURS = max(1, int(os.getenv('MAX_VIDEO_AGE_HOURS', '24')))
# Conservative per-day ceiling for this bot; separate from Google Cloud's actual quota.
DAILY_SEARCH_BUDGET = min(10000, max(1, int(os.getenv('DAILY_SEARCH_BUDGET', '96'))))
RESERVED_SEARCHES = max(0, int(os.getenv('RESERVED_SEARCHES', '24')))
CONFIG_FILE = Path(os.getenv('SEARCH_CONFIG_FILE', 'search_config.json'))
DEFAULT_LEAGUE = os.getenv('TARGET_LEAGUE', '3.30').strip() or '3.30'
DEFAULT_POE2_VERSION = os.getenv('POE2_TARGET_VERSION','1.0').strip() or '1.0'
if not game_modes.valid_poe2_version(DEFAULT_POE2_VERSION):
    raise SystemExit('POE2_TARGET_VERSION musi mieć format X.Y, np. 1.0')
if not features.league_valid(DEFAULT_LEAGUE):
    raise SystemExit('TARGET_LEAGUE musi mieć postać 3.30 albo 3.31')
DAILY_DIGEST_ENABLED = os.getenv('DAILY_DIGEST_ENABLED', 'true').strip().lower() in ('1', 'true', 'yes', 'on', 'tak')
DAILY_DIGEST_TIME = os.getenv('DAILY_DIGEST_TIME', '20:00').strip()
if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', DAILY_DIGEST_TIME):
    raise SystemExit('DAILY_DIGEST_TIME musi mieć format HH:MM, np. 20:00')
DAILY_DIGEST_CHANNEL_ID = int(os.getenv('DAILY_DIGEST_CHANNEL_ID', '0')) or CHANNEL_ID
# YouTube API metadata stays cached for at most seven days by default.
CACHE_RETENTION_DAYS = max(1, min(29, int(os.getenv('YOUTUBE_CACHE_DAYS', '7'))))
# No new personal data fields are added to the consent policy.
POLICY_VERSION = '2026-11-12-v2'
VERSION = enhancements.VERSION
ALERT_CHANNEL_ID = int(os.getenv('ALERT_CHANNEL_ID', str(CHANNEL_ID)))
CHECK_EXTERNAL_LINKS = os.getenv('CHECK_EXTERNAL_LINKS', 'true').lower() in ('true','1','yes','on')
LINK_REFRESH_INTERVAL_HOURS = max(1, int(os.getenv('LINK_REFRESH_INTERVAL_HOURS','6')))
MAX_LINK_REFRESH_PER_RUN = max(1, min(50,int(os.getenv('MAX_LINK_REFRESH_PER_RUN','10'))))
BACKUP_DIR = os.getenv('BACKUP_DIR', str(Path(DB_PATH).parent / 'backups'))
BACKUP_KEEP_DAYS = max(1,min(30,int(os.getenv('BACKUP_KEEP_DAYS','7'))))
VERSION_CHECK_ENABLED = os.getenv('VERSION_CHECK_ENABLED','true').lower() in ('true','1','yes','on')
_health_disconnect_at = None

PRIVACY_URL = 'https://bollek231.github.io/poe-build-notifier-site/privacy.html'
TERMS_URL = 'https://bollek231.github.io/poe-build-notifier-site/terms.html'
# Pacific Time is used to calculate the daily YouTube search quota reset.
PACIFIC = ZoneInfo('America/Los_Angeles')
_health = {'last_start': None, 'last_success': None, 'last_error': None, 'last_results': None}


DEFAULT_CONFIG = {
    'search_queries': [
        'PoE 3.30 build', 'Path of Exile 3.30 league starter',
        'PoE 3.30 build guide', 'Path of Exile 3.30 endgame build',
        'PoE 3.30 leveling build', 'PoE 3.30 bossing build'
    ],
    'exclude_phrases': ['path of exile 2', 'poe 2', 'poe2', 'trailer', 'patch notes',
                        'reaction', 'livestream', 'stream highlights', 'news'],
    'poe2_search_queries': list(game_modes.POE2_QUERY_TEMPLATES),
}
ASCENDANCIES = [
    'Ascendant', 'Slayer', 'Gladiator', 'Champion', 'Assassin', 'Saboteur', 'Trickster',
    'Juggernaut', 'Berserker', 'Chieftain', 'Necromancer', 'Occultist', 'Elementalist',
    'Deadeye', 'Raider', 'Pathfinder', 'Warden', 'Inquisitor', 'Hierophant', 'Guardian',
]
SKILLS = [
    'Lightning Strike', 'Righteous Fire', 'Lightning Arrow', 'Tornado Shot',
    'Explosive Arrow', 'Boneshatter', 'Cyclone', 'Flicker Strike', 'Ice Nova',
    'Frost Blades', 'Molten Strike', 'Toxic Rain', 'Caustic Arrow', 'Spark',
    'Arc', 'Hexblast', 'Detonate Dead', 'Summon Raging Spirit', 'SRS',
    'Blade Vortex', 'Blade Blast', 'Penance Brand', 'Storm Brand', 'Winter Orb',
    'Kinetic Blast', 'Power Siphon', 'Splitting Steel', 'Lacerate', 'Earthshatter',
    'Sunder', 'Ground Slam', 'Volcanic Fissure', 'Fire Trap', 'Explosive Trap',
    'Seismic Trap', 'Poisonous Concoction', 'Essence Drain', 'Contagion',
    'Forbidden Rite', 'Holy Relic', 'Animate Weapon', 'Raise Spectre',
    'Summon Skeletons', 'Viper Strike', 'Dual Strike', 'Reave', 'Cleave',
    'Wild Strike', 'Smite', 'Ice Shot', 'Burning Arrow', 'Elemental Hit',
    'Frostblink', 'Ball Lightning', 'Fireball', 'Freezing Pulse', 'Wave of Conviction',
    'Bladefall', 'Ethereal Knives', 'Poison Spark', 'Tectonic Slam',
]
BUILD_SIGNALS = ['build', 'league starter', 'league start', 'starter', 'pob',
                 'path of building', 'build guide', 'leveling guide', 'endgame guide',
                 'bossing build', 'mapping build']


def utc_now():
    return datetime.now(timezone.utc)


class DailySearchQuotaExceeded(RuntimeError):
    """Official YouTube daily search limit reached; no raw HTTP payload in alerts."""


def quota_message(reset_at):
    timestamp = int(reset_at.timestamp())
    return ('⚠️ **Osiągnięto dzienny limit wyszukiwań YouTube.**\n'
            f'🔄 Reset: <t:{timestamp}:F> (<t:{timestamp}:R>).\n'
            'Bot wznowi wyszukiwanie podczas kolejnego skanu po resecie.')


async def announce_quota_pause(connection, reset_at):
    pause = storage.quota_pause(connection)
    if pause is None or pause[1]:
        return
    try:
        channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)
        await channel.send(quota_message(reset_at), allowed_mentions=discord.AllowedMentions.none())
        storage.mark_quota_notice_sent(connection)
    except Exception:
        log.exception('Nie udało się wysłać krótkiego komunikatu o limicie.')


def parse_time(value):
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return None


def cfg():
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG
    with CONFIG_FILE.open(encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError('search_config.json must contain an object')
    queries = data.get('search_queries', DEFAULT_CONFIG['search_queries'])
    excludes = data.get('exclude_phrases', DEFAULT_CONFIG['exclude_phrases'])
    poe2_queries = data.get('poe2_search_queries', DEFAULT_CONFIG['poe2_search_queries'])
    if not isinstance(queries, list) or not isinstance(excludes, list) or not isinstance(poe2_queries, list):
        raise ValueError('search_queries, poe2_search_queries and exclude_phrases must be lists')
    return {'search_queries': [q.strip() for q in queries if isinstance(q, str) and q.strip()],
            'poe2_search_queries': [q.strip() for q in poe2_queries if isinstance(q,str) and q.strip()],
            'exclude_phrases': [x.lower().strip() for x in excludes if isinstance(x, str) and x.strip()]}


def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    storage.initialize(c)  # Migrates an existing SQLite DB without dropping rows.
    storage.cleanup(c, CACHE_RETENTION_DAYS)
    return c


def norm(value):
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', value.casefold()).split())


def find_term(text, candidates):
    s = ' ' + norm(text) + ' '
    for name in sorted(candidates, key=len, reverse=True):
        if ' ' + norm(name) + ' ' in s:
            return name
    return None


def identify(title, description=''):
    # Prefer title to description: descriptions often include unrelated skill links.
    skill = find_term(title, SKILLS + list(game_modes.POE2_SKILLS)) or find_term(description[:400], SKILLS + list(game_modes.POE2_SKILLS))
    ascendancy = find_term(title, ASCENDANCIES + list(game_modes.POE2_ASCENDANCIES)) or find_term(description[:400], ASCENDANCIES + list(game_modes.POE2_ASCENDANCIES))
    return skill, ascendancy


def classify(title, description, excludes, league, game='poe1'):
    if game == 'poe2':
        # Strict 1.0 mode: never import 0.x guides or unversioned PoE 2 builds.
        if not game_modes.is_target_poe2_guide(title, description, league):
            return None
        skill, asc = identify(title, description)
        category = ('League Starter' if re.search(r'league\s*start|starter',title,re.I) else
                    'Leveling' if re.search(r'level(?:ing|ling)',title,re.I) else
                    'Endgame' if re.search(r'endgame|mapping|bossing',title,re.I) else 'Build')
        return skill,asc,category
    if game != 'poe1':
        return None
    title_lower = title.casefold()
    combined = (title + ' ' + description).casefold()
    # Require the selected league in title or description.
    # A conflicting league version in the title overrides boilerplate in the description.
    if features.title_conflicts_with_league(title, league):
        return None
    if not features.mentions_league(title, description, league):
        return None
    # Description-only league is weaker evidence: require an actual guide/build title.
    if not features.mentions_league(title, '', league) and not any(x in title_lower for x in ('build', 'league starter', 'guide')):
        return None
    if any(term in title_lower for term in excludes) or any(term in description[:600].casefold() for term in ['path of exile 2', 'poe 2', 'poe2']):
        return None
    # Search result must be identifiable as PoE 1, not merely a number.
    if not re.search(r'\b(poe\s*1|poe1|poe|path of exile)\b', combined):
        return None
    if not any(word in combined for word in BUILD_SIGNALS):
        return None
    # Avoid generic news with "build" only in the description.
    skill, asc = identify(title, description)
    if not any(word in title_lower for word in BUILD_SIGNALS) and not skill:
        return None
    if any(word in title_lower for word in ['patch review', 'league reveal', 'announcement', 'tier list', 'top 10']):
        return None
    category = ('League Starter' if 'starter' in combined or 'league start' in combined else
                'Leveling' if 'leveling' in combined else
                'Endgame' if 'endgame' in combined else 'Build')
    return skill, asc, category


def fingerprint(title, skill, asc, league):
    prefix = 'league:' + league + '|'
    if skill and asc:
        return prefix + 'skill:' + norm(skill) + '|asc:' + norm(asc)
    cleaned = norm(title)
    cleaned = re.sub(r'\b(path of exile|poe|build|guide|starter|league|new|updated|best|insane|op|3\s+\d{1,2})\b', ' ', cleaned)
    noise = {'2026', '2027', 'amazing', 'insane', 'ultimate', 'strongest', 'cheap', 'budget', 'fast', 'easy', 'the', 'a', 'for', 'in', 'this', 'is', 'my', 'best', 'new', 'updated', 'league', 'starter', 'guide', 'build', 'poe', 'path', 'of', 'exile', '3', '30'}
    words = [w for w in cleaned.split() if w not in noise]
    return prefix + 'title:' + ' '.join(sorted(set(words)))


def duplicate(c, fp, league):
    rows = c.execute('SELECT fingerprint, league FROM builds WHERE league=?', (league,)).fetchall()
    for row in rows:
        old = row['fingerprint']
        new = fp
        # Pre-update (unprefixed) fingerprints belong to league 3.30.
        if league == '3.30' and not old.startswith('league:'):
            new = fp.removeprefix('league:3.30|')
        if old == new:
            return True
        prefix = 'league:' + league + '|'
        if new.startswith(prefix):
            new = new[len(prefix):]
        if old.startswith(prefix):
            old = old[len(prefix):]
        if new.startswith('title:') and old.startswith('title:'):
            a, b = new[6:], old[6:]
            if min(len(a), len(b)) >= 14 and SequenceMatcher(None, a, b).ratio() >= 0.94:
                return True
    return False


def search_count(c):
    # Google YouTube Data API daily quota resets at midnight Pacific Time.
    start = utc_now().astimezone(PACIFIC).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).isoformat()
    return c.execute('SELECT COUNT(*) FROM search_log WHERE searched_at >= ?', (start,)).fetchone()[0]


def remaining(c, kind):
    reserve = RESERVED_SEARCHES if kind == 'auto' else 0
    return max(0, DAILY_SEARCH_BUDGET - reserve - search_count(c))




def local_quota(c):
    """Current YouTube API method buckets (2026): search.list has a separate
    per-day call quota; non-search methods use the ordinary units budget.
    Ignore legacy search.list unit values (100) in api_usage.
    """
    start = utc_now().astimezone(PACIFIC).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).isoformat()
    other_units = c.execute('SELECT COALESCE(SUM(units),0) FROM api_usage WHERE used_at >= ? AND operation != ?',
                            (start, 'search.list')).fetchone()[0]
    return search_count(c), other_units



def extract_links(description):
    # YouTube API descriptions are plain text; sanitize URLs before Discord buttons.
    found = {}
    for raw in re.findall(r'https?://[^\s<>\]\[)]+', description, re.I):
        raw = raw.rstrip('.,;!\"\'')
        try:
            parsed = urlparse(raw)
            host = (parsed.hostname or '').lower()
            if parsed.scheme not in ('http','https'):
                continue
            if host in ('pobb.in', 'www.pobb.in', 'pastebin.com', 'www.pastebin.com', 'poe.ninja', 'www.poe.ninja') or host.endswith('.pathofbuilding.community'):
                found.setdefault('Path of Building', raw)
            elif host in ('maxroll.gg','www.maxroll.gg') and ('poe' in parsed.path.lower() or 'path-of-exile' in parsed.path.lower()):
                found.setdefault('Maxroll', raw)
            elif features.mobalytics_poe_url(raw):
                found.setdefault('Mobalytics', raw)
        except ValueError:
            continue
    return found


def buttons_from_links(links):
    if not links:
        return None
    view = discord.ui.View(timeout=None)
    for label, url in links.items():
        view.add_item(discord.ui.Button(label=label, style=discord.ButtonStyle.link, url=url))
    return view


def video_buttons(description):
    return buttons_from_links(extract_links(description))


async def video_details(session, video_ids):
    results = {}
    for start in range(0, len(video_ids), 50):
        ids = video_ids[start:start+50]
        params = {'key':API_KEY, 'part':'snippet', 'id':','.join(ids), 'maxResults':50}
        async with session.get('https://www.googleapis.com/youtube/v3/videos', params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
            payload = await response.json(content_type=None)
            if response.status != 200:
                raise RuntimeError(f'YouTube videos.list HTTP {response.status}')
            for item in payload.get('items', []):
                results[item['id']] = item.get('snippet', {})
    return results

# Akceptacja polityki jest zapisywana wyłącznie dla osób wywołujących komendy.
# Widzowie publicznego kanału mogą czytać powiadomienia bez akceptacji;
# kanał nie wymaga roli, a automatyczne skanowanie startuje po uruchomieniu.
async def grant_discord_consent(member, guild):
    if guild is None:
        return False, 'Zgodę można wyrazić tylko na serwerze Discord.'
    connection = db()
    try:
        storage.record_consent(connection, guild.id, member.id, POLICY_VERSION)
    finally:
        connection.close()
    return True, 'Zgoda na dokumenty zapisana. Nie są przyznawane żadne role.'


async def remove_discord_consent(member, guild):
    if guild is None:
        return False, 'Polecenie dostępne tylko na serwerze Discord.'
    connection = db()
    try:
        storage.revoke_consent(connection, guild.id, member.id)
    finally:
        connection.close()
    return True, 'Zgoda wycofana. Nie zmienia to dostępu do publicznego kanału.'


class ConsentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label='Polityka prywatności', style=discord.ButtonStyle.link, url=PRIVACY_URL))
        self.add_item(discord.ui.Button(label='Warunki korzystania', style=discord.ButtonStyle.link, url=TERMS_URL))

    @discord.ui.button(label='Akceptuję zasady', style=discord.ButtonStyle.success, custom_id='poe_privacy_accept_20261112')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, answer = await grant_discord_consent(interaction.user, interaction.guild)
        await interaction.response.send_message(answer, ephemeral=True)

    @discord.ui.button(label='Cofam zgodę', style=discord.ButtonStyle.secondary, custom_id='poe_privacy_revoke_20261112')
    async def revoke(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, answer = await remove_discord_consent(interaction.user, interaction.guild)
        await interaction.response.send_message(answer, ephemeral=True)


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='p', intents=intents, case_insensitive=True, help_command=None)
scan_lock = asyncio.Lock()
digest_lock = asyncio.Lock()


async def search_youtube(session, query):
    params = {'key': API_KEY, 'part': 'snippet', 'q': query, 'type': 'video',
              'order': 'date', 'maxResults': MAX_RESULTS, 'relevanceLanguage': 'en',
              'publishedAfter': (utc_now() - timedelta(hours=MAX_VIDEO_AGE_HOURS)).isoformat().replace('+00:00', 'Z')}
    async with session.get('https://www.googleapis.com/youtube/v3/search', params=params,
                           timeout=aiohttp.ClientTimeout(total=30)) as response:
        payload = await response.json(content_type=None)
        if response.status != 200:
            if storage.is_daily_search_quota_error(response.status, payload):
                raise DailySearchQuotaExceeded('YouTube: Search Queries per day')
            raise RuntimeError(f'YouTube API HTTP {response.status}')
        return payload.get('items', [])


async def alert_admin(key, message, *, cooldown_minutes=60):
    # Deduplicate alerts across restarts. An alert channel may be configured
    # independently of the regular build channel.
    if not ALERT_CHANNEL_ID:
        return False
    c=db()
    try:
        if not storage.alert_allowed(c,key,cooldown_minutes=cooldown_minutes):
            return False
        channel=bot.get_channel(ALERT_CHANNEL_ID) or await bot.fetch_channel(ALERT_CHANNEL_ID)
        await channel.send(discord.utils.escape_mentions(message[:1700]),allowed_mentions=discord.AllowedMentions.none())
        storage.record_alert(c,key)
        return True
    except Exception:
        log.exception('Admin alert could not be delivered')
        return False
    finally:
        c.close()


async def notify_error(message):
    log.error(message)
    _health['last_error'] = {'at':utc_now().isoformat(), 'message':message[:400]}
    await alert_admin('error:'+message.split(':',1)[0][:50],
                      '⚠️ **PoE Bot – problem:** '+discord.utils.escape_mentions(message[:1000]),
                      cooldown_minutes=30)


# Bot nie kasuje, nie edytuje i nie śledzi wieku powiadomień na Discordzie.
# Siedmiodniowy okres dotyczy wyłącznie lokalnych metadanych w SQLite.


async def scan(kind='auto', custom_query=None):
    if scan_lock.locked():
        return None
    async with scan_lock:
        _health['last_start'] = utc_now().isoformat()
        c = db()
        link_session = None
        try:
            config = cfg()
            game = storage.current_game(c)
            league = storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
            query_pool = (game_modes.target_queries(league,config['poe2_search_queries']) if game=='poe2' else
                          features.rendered_queries(config['search_queries'],league))
            queries = [custom_query] if custom_query else query_pool
            pause = storage.quota_pause(c)
            if pause:
                # Official quota is exhausted. No API calls until its PT reset.
                return {'sent': 0, 'searched': 0, 'warning': quota_message(pause[0]), 'quota_exhausted': True}
            channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)
            budget = remaining(c, kind)
            if budget == 0:
                reset = storage.next_search_quota_reset()
                return {'sent': 0, 'searched': 0,
                        'warning': 'Wyczerpano dzienny budżet zapytań tego bota.\n'
                                   + f'Kolejny reset: <t:{int(reset.timestamp())}:F>.',
                        'budget_exhausted': True}
            if kind == 'auto' and custom_query is None:
                # Spread remaining calls across the scans left before midnight PT.
                current_count=search_count(c)
                quota_left=max(0,DAILY_SEARCH_BUDGET-current_count)
                count=enhancements.auto_query_allocation(quota_left,RESERVED_SEARCHES,utc_now(),INTERVAL_H,len(queries))
                try:cursor=int(storage.get_setting(c,'query_cursor_'+game,'0'))
                except ValueError:cursor=0
                queries,next_cursor=enhancements.rotate_queries(queries,min(budget,count),cursor)
                storage.set_setting(c,'query_cursor_'+game,str(next_cursor))
            else:
                queries=queries[:budget]
            filters=storage.get_filters(c,game)
            candidates = {}
            searched = 0
            failures = 0
            quota_exhausted = False
            quota_reset = None
            async with aiohttp.ClientSession() as session:
                for query in queries:
                    # Count before request, including failed attempts: API can charge errors.
                    c.execute('INSERT INTO search_log(searched_at,query,kind) VALUES(?,?,?)',
                              (utc_now().isoformat(), query, kind))
                    c.execute('INSERT INTO api_usage(used_at,units,operation) VALUES(?,?,?)', (utc_now().isoformat(),1,'search.list'))
                    c.commit()
                    searched += 1
                    try:
                        items = await search_youtube(session, query)
                        for item in items:
                            vid = item.get('id', {}).get('videoId')
                            if vid:
                                candidates[vid] = item.get('snippet', {})
                    except DailySearchQuotaExceeded:
                        # Persist the actual 429 before returning; the next scan
                        # won't waste quota or flood Discord with full API errors.
                        failures += 1
                        quota_exhausted = True
                        quota_reset = storage.next_search_quota_reset()
                        storage.begin_quota_pause(c, quota_reset)
                        _health['last_error'] = {'at': utc_now().isoformat(),
                                                 'message': 'Osiągnięto dzienny limit wyszukiwań YouTube.'}
                        log.warning('Dzienny limit Search Queries wyczerpany; reset %s', quota_reset.isoformat())
                        if kind == 'auto':
                            await announce_quota_pause(c, quota_reset)
                        else:
                            # Manual pScan/pSearch replies once via report_scan().
                            storage.mark_quota_notice_sent(c)
                        break
                    except Exception as exc:
                        failures += 1
                        log.exception('Search failed for %s', query)
                        await notify_error(f'Wyszukiwanie nie powiodło się ({query}): {exc}')
                        if 'quotaExceeded' in str(exc) or '403' in str(exc):
                            break
            # videos.list costs one quota unit per batch and provides FULL descriptions;
            # search.list snippets may contain truncated descriptions.
            if candidates:
                try:
                    ids = [vid for vid in candidates if not c.execute('SELECT 1 FROM videos WHERE video_id=?', (vid,)).fetchone()]
                    async with aiohttp.ClientSession() as detail_session:
                        details = await video_details(detail_session, ids)
                    candidates = {vid: info for vid, info in details.items() if vid in candidates}
                    for _ in range((len(ids)+49)//50):
                        c.execute('INSERT INTO api_usage(used_at,units,operation) VALUES(?,?,?)', (utc_now().isoformat(),1,'videos.list'))
                    c.commit()
                except Exception as exc:
                    # Fail closed: no full descriptions -> don't publish possibly old league videos.
                    await notify_error(f'Nie udało się pobrać pełnych opisów filmów: {exc}')
                    return {'sent':0,'searched':searched,'warning':'Brak opisów filmów; publikacja wstrzymana.'}
            sent = 0
            link_session=aiohttp.ClientSession()
            # Oldest first. Always verify age locally, even if YouTube search
            # returned a video outside the requested publishedAfter window.
            for vid, info in sorted(candidates.items(), key=lambda it: (
                0 if storage.channel_rule(c,it[1].get('channelId',''))=='allow' else 1,
                it[1].get('publishedAt', ''))):
                published = parse_time(info.get('publishedAt'))
                if published is None or not (utc_now() - timedelta(hours=MAX_VIDEO_AGE_HOURS) <= published <= utc_now() + timedelta(minutes=2)):
                    continue
                if c.execute('SELECT 1 FROM videos WHERE video_id=?', (vid,)).fetchone():
                    continue
                channel_id=info.get('channelId','')
                channel_rule=storage.channel_rule(c,channel_id)
                if channel_rule=='block' or (storage.get_setting(c,'allowlist_only','false')=='true' and channel_rule!='allow'):
                    continue
                title = info.get('title', 'Film YouTube')
                description = info.get('description', '')
                result = classify(title, description, config['exclude_phrases'], league, game)
                if result is None:
                    continue
                skill, asc, category = result
                # Trust list prioritizes, but never bypasses league, age, PoE1 or user filters.
                if not enhancements.matches_filters(title,description,skill,asc,category,filters):
                    continue
                fp = fingerprint(title, skill, asc, league)
                if duplicate(c, fp, league):
                    # Mark as seen to avoid rechecking it, but do not add a new build.
                    c.execute('INSERT OR IGNORE INTO videos VALUES(?,?,?,?,?)',
                              (vid, title, f'https://www.youtube.com/watch?v={vid}',
                               info.get('publishedAt'), utc_now().isoformat()))
                    c.commit()
                    continue
                url = f'https://www.youtube.com/watch?v={vid}'
                embed = discord.Embed(title=title[:256], url=url, color=discord.Color.dark_purple())
                embed.add_field(name='Gra', value=game_modes.game_label(game), inline=True)
                embed.add_field(name='Liga / wersja', value=league, inline=True)
                embed.add_field(name='Twórca na YouTube', value=info.get('channelTitle', 'Nieznany')[:1024], inline=False)
                embed.add_field(name='Umiejętność (oznaczenie bota)', value=skill or 'Nie rozpoznano', inline=True)
                embed.add_field(name='Ascendancy (oznaczenie bota)', value=asc or 'Nie rozpoznano', inline=True)
                embed.add_field(name='Kategoria (oznaczenie bota)', value=category, inline=True)
                if published:
                    stamp = int(published.timestamp())
                    embed.add_field(name='Opublikowano na YouTube', value=f'<t:{stamp}:F>\n<t:{stamp}:R>', inline=False)
                embed.add_field(name='Źródło', value='[Oryginalny film w YouTube](' + url + ')', inline=False)
                thumb = info.get('thumbnails', {}).get('high') or info.get('thumbnails', {}).get('medium')
                if thumb and thumb.get('url'):
                    embed.set_thumbnail(url=thumb['url'])
                embed.set_footer(text='Dane filmu: YouTube • Kategorie ustala bot, nie YouTube • Zasady: pPrivacy')
                try:
                    links=extract_links(description)
                    if CHECK_EXTERNAL_LINKS:
                        links=await services.verified_links(link_session,c,links)
                    else:
                        links={label:target for label,target in links.items() if enhancements.sane_external_url(target)}
                    if sent:
                        await asyncio.sleep(SEND_DELAY)
                    posted_message=await channel.send(content=url, embed=embed, view=buttons_from_links(links))
                    c.execute('INSERT OR IGNORE INTO videos VALUES(?,?,?,?,?)',
                              (vid, title, url, info.get('publishedAt'), utc_now().isoformat()))
                    c.execute('INSERT OR IGNORE INTO builds(fingerprint,canonical_title,first_video_id,created_at,league) VALUES(?,?,?,?,?)',
                              (fp, title, vid, utc_now().isoformat(), league))
                    c.execute('INSERT OR REPLACE INTO video_metadata VALUES(?,?,?,?)',
                              (vid, skill, asc, category))
                    c.commit()
                    # New posts only; previously sent Discord messages stay untouched.
                    storage.record_post(c,vid,channel.id,posted_message.id,links)
                    sent += 1
                except discord.HTTPException as exc:
                    await notify_error(f'Nie udało się wysłać filmu na Discord: {exc}')
                    break
            result = {'sent': sent, 'searched': searched,
                      'warning': quota_message(quota_reset) if quota_exhausted
                                 else (f'Nieudane wyszukiwania: {failures}' if failures else ''),
                      'quota_exhausted': quota_exhausted}
            _health['last_success'] = utc_now().isoformat() if not failures else _health['last_success']
            _health['last_results'] = result
            return result
        finally:
            if link_session is not None:
                await link_session.close()
            c.close()


def format_digest_pages(rows, league, local_day, game='poe1'):
    """One to three embeds, no external requests. Split to fit Discord size limits."""
    header = f'Buildy wysłane na Discorda w ciągu poprzednich 24 godzin • {local_day}'
    heading = f'📚 Podsumowanie buildów {game_modes.game_label(game)} {league}'
    if not rows:
        return [discord.Embed(title=heading,
                              description=header + '\n\nBrak nowych buildów w tym okresie.',
                              color=discord.Color.dark_purple())]
    chunks = []
    page = ''
    for row in rows:
        title = discord.utils.escape_markdown(row['canonical_title'][:104])
        title = discord.utils.escape_mentions(title).replace('\n', ' ')
        skill = discord.utils.escape_markdown((row['skill'] or 'Nie rozpoznano')[:45])
        asc = discord.utils.escape_markdown((row['ascendancy'] or 'Nie rozpoznano')[:45])
        category = discord.utils.escape_markdown((row['classification'] or 'Build')[:25])
        vid = row['first_video_id']
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid):
            continue
        line = f'• **{category}** | [{title}](https://youtu.be/{vid})\n  {skill} · {asc}\n'
        if page and len(page) + len(line) > 2900:
            chunks.append(page)
            page = ''
        page += line
    if page:
        chunks.append(page)
    embeds = []
    for i, chunk in enumerate(chunks):
        suffix = f' ({i+1}/{len(chunks)})' if len(chunks) > 1 else ''
        embed = discord.Embed(title=heading + suffix,
                              description=header + '\n\n' + chunk,
                              color=discord.Color.dark_purple())
        embed.set_footer(text='Źródło: YouTube • Zestawienie przygotował bot • Bez dodatkowych zapytań API')
        embeds.append(embed)
    return embeds or [discord.Embed(title=heading,description='Brak wpisów do wyświetlenia.')]


async def send_digest(*, manual=False):
    """Automatically send once per Polish date. Manual preview does not mark it sent."""
    if digest_lock.locked():
        return 'Podsumowanie jest już przygotowywane.' if manual else None
    async with digest_lock:
        current = utc_now()
        today = current.astimezone(features.POLAND).date().isoformat()
        c = db()
        try:
            game=storage.current_game(c)
            digest_channel_key = f'{DAILY_DIGEST_CHANNEL_ID}:{game}'
            if not manual and storage.digest_sent_date(c, digest_channel_key, today):
                return None
            league=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
            start, end = features.digest_window(current)
            rows = storage.digest_builds(c, league, start, end, limit=100)
            embeds = format_digest_pages(rows, league, today,game)
            channel = bot.get_channel(DAILY_DIGEST_CHANNEL_ID) or await bot.fetch_channel(DAILY_DIGEST_CHANNEL_ID)
            for index, embed in enumerate(embeds):
                if index:
                    await asyncio.sleep(SEND_DELAY)
                await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            if not manual:
                storage.mark_digest_sent(c, digest_channel_key, today, sent_at=current)
            return f'Podsumowanie {game_modes.game_label(game)} {league}: {len(rows)} buildów z ostatnich 24 godzin.'
        finally:
            c.close()


@tasks.loop(minutes=1)
async def automatic_digest():
    if not DAILY_DIGEST_ENABLED or scan_lock.locked():
        # Wait for the current scan so the digest includes newly posted builds.
        return
    now = utc_now()
    local_day = now.astimezone(features.POLAND).date().isoformat()
    c = db()
    try:
        current_game=storage.current_game(c)
        last = local_day if storage.digest_sent_date(c, f'{DAILY_DIGEST_CHANNEL_ID}:{current_game}', local_day) else None
    finally:
        c.close()
    if not features.digest_due(now, DAILY_DIGEST_TIME, last):
        return
    try:
        await send_digest(manual=False)
    except Exception as exc:
        log.exception('Codzienne podsumowanie nie powiodło się')
        _health['last_error'] = {'at':utc_now().isoformat(), 'message':f'Podsumowanie: {exc}'[:350]}
        # No Discord spam. Retry at next tick; no extra YouTube API requests.


@automatic_digest.before_loop
async def digest_wait_ready():
    await bot.wait_until_ready()


@tasks.loop(hours=INTERVAL_H)
async def automatic_scan():
    try:
        await scan('auto')
    except Exception as exc:
        log.exception('Automatic scan error')
        await notify_error(f'Automatyczne skanowanie: {exc}')


@automatic_scan.before_loop
async def wait_ready():
    await bot.wait_until_ready()


async def refresh_post_links(*, manual=False):
    """Inspect only tracked recent posts (up to seven days). Add missing buttons
    by EDITING the existing Discord message, never deleting/reposting it.
    """
    if scan_lock.locked():return 'Skanowanie w toku; ponów później.'
    c=db()
    try:
        cutoff=utc_now() - timedelta(hours=LINK_REFRESH_INTERVAL_HOURS if not manual else 0)
        rows=storage.refresh_candidates(c,cutoff=cutoff,limit=MAX_LINK_REFRESH_PER_RUN)
        if not rows:return 'Brak powiadomień wymagających sprawdzenia.'
        updated=0
        async with aiohttp.ClientSession() as session:
            for offset in range(0,len(rows),50):
                batch=rows[offset:offset+50]
                details=await video_details(session,[row['video_id'] for row in batch])
                c.execute('INSERT INTO api_usage(used_at,units,operation) VALUES(?,?,?)',(utc_now().isoformat(),1,'videos.list'))
                c.commit()
                for row in batch:
                    vid=row['video_id']
                    info=details.get(vid)
                    if not info:
                        storage.update_post_links(c,vid,None)
                        continue
                    try:previous=json.loads(row['links_json'])
                    except (ValueError,TypeError):previous={}
                    fresh=extract_links(info.get('description',''))
                    if CHECK_EXTERNAL_LINKS:
                        fresh=await services.verified_links(session,c,fresh)
                    else:
                        fresh={k:v for k,v in fresh.items() if enhancements.sane_external_url(v)}
                    if not enhancements.links_changed(previous,fresh):
                        storage.update_post_links(c,vid,None)
                        continue
                    merged=enhancements.merged_links(previous,fresh)
                    try:
                        destination=bot.get_channel(int(row['channel_id'])) or await bot.fetch_channel(int(row['channel_id']))
                        message=await destination.fetch_message(int(row['message_id']))
                        await message.edit(view=buttons_from_links(merged))
                        storage.update_post_links(c,vid,merged)
                        updated+=1
                        await asyncio.sleep(min(SEND_DELAY,3))
                    except discord.NotFound:
                        # Message removed by a human; do not repost or delete anything.
                        storage.remove_post_tracking(c,vid)
                    except discord.HTTPException as error:
                        log.warning('Cannot edit links for video %s: %s',vid,type(error).__name__)
                        storage.update_post_links(c,vid,None)
        return f'Zbadano {len(rows)} powiadomień, uzupełniono przyciski w {updated} wiadomościach.'
    finally:
        c.close()


@tasks.loop(hours=LINK_REFRESH_INTERVAL_HOURS)
async def automatic_link_refresh():
    try:
        await refresh_post_links()
    except Exception as exc:
        log.exception('Refresh links failed')
        await notify_error(f'Odświeżanie linków: {type(exc).__name__}')


@automatic_link_refresh.before_loop
async def link_refresh_wait_ready():
    await bot.wait_until_ready()


@tasks.loop(hours=12)
async def automatic_backup():
    try:
        dest,created=await asyncio.to_thread(backups.backup_database,DB_PATH,BACKUP_DIR,
                                              keep=BACKUP_KEEP_DAYS,now=utc_now())
        if created:log.info('Private SQLite backup created: %s',dest)
    except Exception as exc:
        log.exception('Backup failed')
        await notify_error(f'Kopia SQLite: {type(exc).__name__}')


@automatic_backup.before_loop
async def backup_wait_ready():
    await bot.wait_until_ready()


async def check_new_version(*, announce=True):
    async with aiohttp.ClientSession() as session:
        latest=await services.latest_public_version(session)
    if latest is None:return None
    if announce and enhancements.is_newer(latest, VERSION):
        c=db()
        try:
            prev=storage.get_setting(c,'last_notified_version','')
            if prev!=latest:
                delivered=await alert_admin('new_version_'+latest,
                    f'🆕 **Dostępna aktualizacja PoE Build Notifier v{latest}** (obecnie v{VERSION}).\n'
                    '📋 https://bollek231.github.io/poe-build-notifier-site/changelog.html\n'
                    'Bot nie aktualizuje się automatycznie.',cooldown_minutes=60)
                if delivered:storage.set_setting(c,'last_notified_version',latest)
        finally:
            c.close()
    return latest


@tasks.loop(hours=12)
async def automatic_version_check():
    if VERSION_CHECK_ENABLED:
        try:await check_new_version()
        except Exception:log.exception('Could not check latest version')


@automatic_version_check.before_loop
async def version_wait_ready():
    await bot.wait_until_ready()


@bot.event
async def on_disconnect():
    global _health_disconnect_at
    if _health_disconnect_at is None:_health_disconnect_at=utc_now()


@bot.event
async def on_resumed():
    global _health_disconnect_at
    if _health_disconnect_at is not None:
        downtime=utc_now()-_health_disconnect_at
        _health_disconnect_at=None
        if downtime.total_seconds()>15:
            await alert_admin('connection_restored','✅ **PoE Bot: połączenie z Discordem odzyskane.**',
                              cooldown_minutes=10)


@bot.event
async def on_ready():
    global _health_disconnect_at
    log.info('Connected as %s', bot.user)
    first_ready=not getattr(bot,'_first_connection_reported',False)
    if first_ready:
        bot._first_connection_reported=True
        await alert_admin('service_started','✅ **PoE Build Notifier v'+VERSION+' działa.** '
                          'Bot uruchomiony lub ponownie uruchomiony.',cooldown_minutes=10)
    elif _health_disconnect_at is not None:
        _health_disconnect_at=None
        await alert_admin('connection_restored','✅ **PoE Bot: połączenie z Discordem odzyskane.**',cooldown_minutes=10)
    if not getattr(bot, '_privacy_view_registered', False):
        bot.add_view(ConsentView())
        bot._privacy_view_registered = True
    if not automatic_scan.is_running():
        automatic_scan.start()
    if DAILY_DIGEST_ENABLED and not automatic_digest.is_running():
        automatic_digest.start()
    if not automatic_link_refresh.is_running():
        automatic_link_refresh.start()
    if not automatic_backup.is_running():
        automatic_backup.start()
    if VERSION_CHECK_ENABLED and not automatic_version_check.is_running():
        automatic_version_check.start()


def allowed(ctx):
    return ctx.channel.id == CHANNEL_ID and ctx.guild is not None and ctx.author.guild_permissions.manage_guild


async def require_consent(ctx):
    c = db()
    try:
        agreed = ctx.guild is not None and storage.has_consent(c, ctx.guild.id, ctx.author.id, POLICY_VERSION)
    finally:
        c.close()
    if not agreed:
        await ctx.reply('Najpierw zaakceptuj politykę prywatności. Wpisz `pPrivacy`, a następnie kliknij „Akceptuję zasady” lub użyj `pAgree`.')
    return agreed


@bot.command(name='Privacy', aliases=['Zasady'])
@commands.guild_only()
async def privacy_command(ctx):
    await ctx.reply('**PoE Build Notifier — zgoda i dokumenty**\n'
                    'Bot przetwarza publiczne informacje o filmach z YouTube, a także minimalne informacje o zgodzie na Discordzie. '
                    'Przed korzystaniem z komend administratora zapoznaj się z polityką prywatności i warunkami korzystania. '
                    'Kliknij „Akceptuję zasady”, aby korzystać z komend administracyjnych. Powiadomienia na Discordzie pozostają dostępne na dotychczasowym kanale.',
                    view=ConsentView(), allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Agree', aliases=['Zgoda'])
@commands.guild_only()
async def agree_command(ctx):
    ok, message = await grant_discord_consent(ctx.author, ctx.guild)
    await ctx.reply(message, allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Revoke', aliases=['CofnijZgode'])
@commands.guild_only()
async def revoke_command(ctx):
    ok, message = await remove_discord_consent(ctx.author, ctx.guild)
    await ctx.reply(message, allowed_mentions=discord.AllowedMentions.none())


async def report_scan(ctx, custom=None):
    if scan_lock.locked():
        await ctx.reply('Skanowanie już trwa. Poczekaj na jego zakończenie.')
        return
    # Avoid 'search starting' noise if we've already learned Google's quota is exhausted.
    connection = db()
    try:
        pause = storage.quota_pause(connection)
    finally:
        connection.close()
    if pause:
        await ctx.reply(quota_message(pause[0]), allowed_mentions=discord.AllowedMentions.none())
        return
    await ctx.reply('🔎 Rozpoczynam wyszukiwanie YouTube…')
    try:
        result = await scan('manual', custom)
        if result is None:
            await ctx.reply('Skanowanie już trwa.')
        elif result.get('quota_exhausted') or result.get('budget_exhausted'):
            await ctx.reply(result['warning'], allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.reply(f"Skan zakończony. Nowe filmy: **{result['sent']}**. "
                            f"Wykonane wyszukiwania: **{result['searched']}**. "
                            + result['warning'])
    except Exception as exc:
        log.exception('Manual scan error')
        await notify_error(f'Ręczne skanowanie: {exc}')
        await ctx.reply('Wystąpił błąd skanowania. Sprawdź komunikat bota.')


@bot.command(name='Scan')
@commands.check(allowed)
async def scan_command(ctx):
    if await require_consent(ctx):
        await report_scan(ctx)


@bot.command(name='Search')
@commands.check(allowed)
async def search_command(ctx, *, query: str = ''):
    if not await require_consent(ctx):
        return
    query = query.strip()
    if len(query) < 3 or len(query) > 100:
        await ctx.reply('Użycie: `pSearch Lightning Strike Slayer` (3–100 znaków).')
        return
    c = db()
    try:
        game=storage.current_game(c)
        league=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
    finally:
        c.close()
    label = 'PoE 2' if game=='poe2' else 'PoE'
    await report_scan(ctx, f'{label} {league} {query} build')


@bot.command(name='Limit')
@commands.check(allowed)
async def limit_command(ctx):
    if not await require_consent(ctx):
        return
    c = db()
    try:
        searches, other_units = local_quota(c)
        auto_remaining = max(0, DAILY_SEARCH_BUDGET - RESERVED_SEARCHES - searches)
        game=storage.current_game(c)
        queries=cfg()
        total_queries=len(queries['poe2_search_queries'] if game=='poe2' else queries['search_queries'])
        next_auto = enhancements.auto_query_allocation(max(0,DAILY_SEARCH_BUDGET-searches),
                         RESERVED_SEARCHES,utc_now(),INTERVAL_H,total_queries)
        daily_remaining = max(0, DAILY_SEARCH_BUDGET - searches)
        pause = storage.quota_pause(c)
        if pause:
            await ctx.reply('📊 **YouTube API**\n' + quota_message(pause[0]) +
                            '\nLokalny licznik: **' + str(searches) + '** wyszukiwań; '
                            'nie jest oficjalnym odczytem Google.',
                            allowed_mentions=discord.AllowedMentions.none())
            return
        await ctx.reply(
            '📊 **YouTube API – licznik lokalny**\n'
            f'Wyszukiwania: **{searches}/{DAILY_SEARCH_BUDGET}** dzisiaj.\n'
            f'Pozostało w budżecie bota: **{daily_remaining}** wyszukiwań.\n'
            f'Dostępne dla skanów automatycznych: **{auto_remaining}**.\n'
            f'Plan na kolejny skan: **{next_auto}** zapytań (rotacja fraz).\n'
            f'Rezerwa na ręczne komendy: **{RESERVED_SEARCHES}**.\n'
            f'Pozostałe operacje YouTube API: **{other_units}** szacowanych jednostek.\n'
            'ℹ️ To licznik tego bota, nie oficjalny odczyt limitów Google; '
            'nie obejmuje zapytań innych aplikacji.',
            allowed_mentions=discord.AllowedMentions.none()
        )
    finally:
        c.close()


@bot.command(name='Health')
@commands.check(allowed)
async def health_command(ctx):
    if not await require_consent(ctx):
        return
    info = _health
    connection = db()
    try:
        pause = storage.quota_pause(connection)
        digest_today = storage.digest_sent_date(connection, f'{DAILY_DIGEST_CHANNEL_ID}:{storage.current_game(connection)}', utc_now().astimezone(features.POLAND).date().isoformat())
    finally:
        connection.close()
    quota_status = ('Wyczerpany do <t:' + str(int(pause[0].timestamp())) + ':F>') if pause else 'Brak potwierdzonego wyczerpania'
    await ctx.reply('🩺 **Stan bota v'+VERSION+'**\n'
                    f'Codzienne podsumowanie: **{"wysłano dziś" if digest_today else "jeszcze nie wysłano"}** (godz. {DAILY_DIGEST_TIME} PL)\n'
                    f'Limit wyszukiwań YouTube: **{quota_status}**\n'
                    f'Połączenie Discord: **{ "OK" if bot.is_ready() else "Niedostępne" }**\n'
                    f'Automatyczny skan: **{ "aktywny" if automatic_scan.is_running() else "nieaktywny" }**\n'
                    f'Skan trwa: **{ "tak" if scan_lock.locked() else "nie" }**\n'
                    f'Ostatni start: `{info["last_start"] or "brak"}`\n'
                    f'Ostatni udany skan: `{info["last_success"] or "brak"}`\n'
                    f'Ostatni błąd: `{str(info["last_error"])[:300] if info["last_error"] else "brak"}`')


@bot.command(name='Builds')
@commands.check(allowed)
async def builds_command(ctx):
    if not await require_consent(ctx):
        return
    c = db()
    try:
        game=storage.current_game(c)
        league = storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        rows = c.execute('SELECT canonical_title, first_video_id FROM builds WHERE league=? ORDER BY created_at DESC LIMIT 10', (league,)).fetchall()
        if not rows:
            await ctx.reply('Brak zapisanych buildów.')
            return
        lines = [f'{i}. {discord.utils.escape_mentions(r["canonical_title"][:100])} — https://youtu.be/{r["first_video_id"]}'
                 for i, r in enumerate(rows, 1)]
        await ctx.reply(f'**Ostatnie buildy (historia w bazie z ostatnich {CACHE_RETENTION_DAYS} dni):**\n' + '\n'.join(lines), allowed_mentions=discord.AllowedMentions.none())
    finally:
        c.close()


@bot.command(name='Settings')
@commands.check(allowed)
async def settings_command(ctx):
    if not await require_consent(ctx):
        return
    config = cfg()
    c = db()
    try:
        game=storage.current_game(c)
        league=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
    finally:
        c.close()
    number_of_queries=len(config['poe2_search_queries'] if game=='poe2' else config['search_queries'])
    await ctx.reply(f'⚙️ **Ustawienia v{VERSION}**\n'
                    f'Gra: **{game_modes.game_label(game)}** (zmiana: `pGame poe1` / `pGame poe2`)\n'
                    f'Wersja: **{league}** (zmiana: `pLeague {"1.0" if game=="poe2" else "3.31"}`)\n'
                    f'Podsumowanie: **{DAILY_DIGEST_TIME} czasu polskiego** ({"włączone" if DAILY_DIGEST_ENABLED else "wyłączone"})\n'
                    f'Automatyczny skan: co **{INTERVAL_H} h**\n'
                    f'Frazy: **{number_of_queries}**\n'
                    f'Wyniki na frazę: **{MAX_RESULTS}**\n'
                    f'Odstęp wiadomości: **{SEND_DELAY:g} s**\n'
                    f'Budżet: **{DAILY_SEARCH_BUDGET}** zapytań / dzień PT\n'
                    f'Wiek filmu: **maksymalnie {MAX_VIDEO_AGE_HOURS} h**\n'
                    f'Przechowywanie metadanych: **{CACHE_RETENTION_DAYS} dni**\n'
                    'Zgoda na komendy: `pPrivacy`, `pAgree`, `pRevoke` (bez dodatkowej roli)\n'
                    'Wiadomości Discord: pozostają na kanale; bot ich nie usuwa\n'
                    f'Filtry: {game_modes.game_label(game)} / {league} / build, filtr 24h, odrzucanie starszych wersji.')


@bot.command(name='Game')
@commands.check(allowed)
async def game_command(ctx, *, selected: str=''):
    """Switch PoE 1 / PoE 2 without a restart. Persistent across restarts."""
    if not await require_consent(ctx):return
    c=db()
    try:
        game=storage.current_game(c)
        version=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        if not selected.strip():
            await ctx.reply(f'🎮 Gra: **{game_modes.game_label(game)}**, wersja **{version}**.\n'
                            'Przełącz: pGame poe2 lub pGame poe1.')
            return
        new=game_modes.normalize_game(selected)
        if new is None:
            await ctx.reply('Użycie: pGame poe1 lub pGame poe2.')
            return
        if scan_lock.locked():
            await ctx.reply('Skanowanie trwa. Zmień grę po zakończeniu bieżącego skanu.')
            return
        if game==new:
            await ctx.reply(f'🎮 **{game_modes.game_label(game)} {version}** jest już aktywne.')
            return
        storage.set_game(c,new)
        new_version=storage.current_game_version(c,new,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        await ctx.reply(f'✅ Przełączono grę na **{game_modes.game_label(new)} {new_version}**.\n'
                        'Od teraz pScan, pSearch, automatyczne skanowanie i podsumowanie używają tej gry. '
                        'Poprzednia wersja drugiej gry pozostaje zapamiętana. Restart nie jest wymagany.')
    finally:
        c.close()


@bot.command(name='League')
@commands.check(allowed)
async def league_command(ctx, *, version: str=''):
    if not await require_consent(ctx):return
    c=db()
    try:
        game=storage.current_game(c)
        current=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        new=version.strip()
        sample='1.0' if game=='poe2' else '3.31'
        if not new:
            await ctx.reply(f'Gra: **{game_modes.game_label(game)}**. Aktualna wersja: **{current}**. '
                            f'Zmiana: pLeague {sample}.')
            return
        valid=game_modes.valid_poe2_version(new) if game=='poe2' else features.league_valid(new)
        if not valid:
            await ctx.reply(f'Niepoprawny numer wersji dla {game_modes.game_label(game)}. '
                            f'Użyj np. pLeague {sample}.')
            return
        if scan_lock.locked():
            await ctx.reply('Skanowanie trwa. Zmień wersję po jego zakończeniu.')
            return
        if new==current:
            await ctx.reply(f'Wersja **{new}** jest już aktywna.')
            return
        storage.set_game_version(c,game,new)
        await ctx.reply(f'✅ {game_modes.game_label(game)}: wersja **{current}** → **{new}**.\n'
                        'Wyszukiwanie i filtry już korzystają z nowej wersji. '
                        'Nie zmieniono ustawień drugiej gry ani historii wysłanych filmów.')
    finally:
        c.close()


@bot.command(name='Digest', aliases=['Podsumowanie'])
@commands.check(allowed)
async def digest_command(ctx):
    if not await require_consent(ctx):
        return
    try:
        message = await send_digest(manual=True)
        await ctx.reply(message or 'Podsumowanie zostało wysłane.', allowed_mentions=discord.AllowedMentions.none())
    except Exception:
        log.exception('Ręczne podsumowanie nie powiodło się')
        await ctx.reply('Nie udało się wysłać podsumowania. Sprawdź logi bota.')


@bot.command(name='BlockChannel')
@commands.check(allowed)
async def block_channel_command(ctx, *, channel: str=''):
    if not await require_consent(ctx):return
    ident=enhancements.youtube_channel_id(channel)
    if not ident:
        await ctx.reply('Podaj ID kanału YouTube: `pBlockChannel UCxxxxxxxxxxxxxxxxxxxxxx` (lub jego URL /channel/UC...).')
        return
    c=db()
    try:storage.put_channel_rule(c,ident,'block')
    finally:c.close()
    await ctx.reply(f'⛔ Zablokowano kanał YouTube `{ident}`. Nie będzie publikowany.')


@bot.command(name='AllowChannel')
@commands.check(allowed)
async def allow_channel_command(ctx, *, channel: str=''):
    if not await require_consent(ctx):return
    ident=enhancements.youtube_channel_id(channel)
    if not ident:
        await ctx.reply('Podaj ID kanału YouTube: `pAllowChannel UCxxxxxxxxxxxxxxxxxxxxxx`.')
        return
    c=db()
    try:storage.put_channel_rule(c,ident,'allow')
    finally:c.close()
    await ctx.reply(f'✅ Zaufany kanał `{ident}`. Priorytet kolejności, ale wszystkie filtry nadal obowiązują.')


@bot.command(name='UnlistChannel')
@commands.check(allowed)
async def unlist_channel_command(ctx, *, channel: str=''):
    if not await require_consent(ctx):return
    ident=enhancements.youtube_channel_id(channel)
    if not ident:
        await ctx.reply('Użycie: `pUnlistChannel UCxxxxxxxxxxxxxxxxxxxxxx`.')
        return
    c=db()
    try:removed=storage.delete_channel_rule(c,ident)
    finally:c.close()
    await ctx.reply('Usunięto regułę kanału.' if removed else 'Kanału nie było na żadnej liście.')


@bot.command(name='Whitelist')
@commands.check(allowed)
async def whitelist_command(ctx, mode: str=''):
    if not await require_consent(ctx):return
    c=db()
    try:
        if mode.casefold() in ('on','only'):
            if not any(r[1]=='allow' for r in storage.all_channel_rules(c)):
                await ctx.reply('Najpierw dodaj zaufany kanał: `pAllowChannel UC...`.')
                return
            storage.set_setting(c,'allowlist_only','true')
        elif mode.casefold()=='off':
            storage.set_setting(c,'allowlist_only','false')
        elif mode:
            await ctx.reply('Użycie: `pWhitelist on` (publikuj tylko zaufane kanały) lub `pWhitelist off`.')
            return
        value=storage.get_setting(c,'allowlist_only','false')=='true'
    finally:c.close()
    await ctx.reply('✅ Biała lista: **tylko zaufane kanały**.' if value else
                    'ℹ️ Biała lista: **priorytet zaufanych, pozostałe dozwolone** (poza zablokowanymi).')


@bot.command(name='ChannelRules')
@commands.check(allowed)
async def channel_rules_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:rules=storage.all_channel_rules(c)
    finally:c.close()
    lines=[f'{"✅ zaufany" if r[1]=="allow" else "⛔ zablokowany"}: `{r[0]}`' for r in rules[:35]]
    await ctx.reply('📃 **Lista kanałów YouTube**\n'+('\n'.join(lines) if lines else 'Brak reguł.') +
                    ('\n… i kolejne.' if len(rules)>35 else ''),allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Filters')
@commands.check(allowed)
async def filters_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:f=storage.get_filters(c,storage.current_game(c))
    finally:c.close()
    values=', '.join(f'**{k}**: `{v}`' for k,v in f.items()) or 'brak (wszystkie zgodne buildy)'
    await ctx.reply('🎯 **Filtry buildów**\n'+values+'\nPrzykłady: `pFilter skill Lightning Strike`, '
                    '`pFilter ascendancy Deadeye`, `pFilter class Ranger`, '
                    '`pFilter mode SSF`, `pFilter stage starter`; `pFilter clear`.')


@bot.command(name='Filter')
@commands.check(allowed)
async def filter_command(ctx, field: str='', *, value: str=''):
    if not await require_consent(ctx):return
    field=field.casefold().strip()
    if field=='clear':
        c=db()
        try:storage.set_filters(c,{},storage.current_game(c))
        finally:c.close()
        await ctx.reply('✅ Wyczyszczono wszystkie rozszerzone filtry.')
        return
    c=db()
    try:active_game=storage.current_game(c)
    finally:c.close()
    available_skills=SKILLS+list(game_modes.POE2_SKILLS) if active_game=='poe2' else SKILLS
    available_asc=ASCENDANCIES+list(game_modes.POE2_ASCENDANCIES) if active_game=='poe2' else ASCENDANCIES
    try:canonical=enhancements.validate_filter(field,value,available_skills,available_asc)
    except ValueError:
        await ctx.reply('Wybierz: `skill`, `ascendancy`, `class`, `mode` (SSF/HC/SC), '
                        '`stage` (starter/endgame/leveling/build). Wpisz `all`, by usunąć wybrany filtr.')
        return
    c=db()
    try:
        all_filters=storage.get_filters(c,active_game)
        if canonical is None:all_filters.pop(field,None)
        else:all_filters[field]=canonical
        storage.set_filters(c,all_filters,active_game)
    finally:c.close()
    await ctx.reply(f'✅ Filtr `{field}`: `{canonical or "wszystkie"}`. Zmiana obowiązuje przy następnym skanie.')


@bot.command(name='RefreshLinks')
@commands.check(allowed)
async def refresh_links_command(ctx):
    if not await require_consent(ctx):return
    await ctx.reply('🔗 Sprawdzam linki w ostatnio opublikowanych filmach…')
    try:reply=await refresh_post_links(manual=True)
    except Exception as exc:
        log.exception('Manual refresh error')
        reply=f'Nie udało się odświeżyć przycisków ({type(exc).__name__}).'
    await ctx.reply(reply,allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Backup')
@commands.check(allowed)
async def backup_command(ctx):
    if not await require_consent(ctx):return
    try:
        path,created=await asyncio.to_thread(backups.backup_database,DB_PATH,BACKUP_DIR,
                                             keep=BACKUP_KEEP_DAYS,now=utc_now())
        await ctx.reply('💾 **Kopia SQLite**: '+('utworzona' if created else 'już istnieje dzisiaj')+
                        f'. Folder: `{discord.utils.escape_mentions(str(path.parent))}`. '
                        'Plik nie jest publikowany na GitHubie.')
    except Exception as exc:
        log.exception('Manual backup error')
        await ctx.reply(f'Błąd kopii zapasowej ({type(exc).__name__}). Sprawdź logi.')


@bot.command(name='Version')
@commands.check(allowed)
async def version_command(ctx):
    if not await require_consent(ctx):return
    remote=await check_new_version(announce=False)
    if not remote:
        status='Nie udało się sprawdzić najnowszej wersji (brak połączenia z GitHubem).'
    elif enhancements.is_newer(remote,VERSION):
        status=f'🆕 Dostępna aktualizacja **v{remote}**.'
    else:
        status=f'Aktualna publiczna wersja: **v{remote}**.'
    await ctx.reply(f'📦 **PoE Build Notifier v{VERSION}**\n{status}\n'
                    '📋 https://bollek231.github.io/poe-build-notifier-site/changelog.html\n'
                    'Bot sam nie pobiera ani nie instaluje aktualizacji.',allowed_mentions=discord.AllowedMentions.none())


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return  # Ignore unauthorized command invocations.
    if isinstance(error, commands.CommandNotFound):
        return
    log.error('Command error: %s', error)
    await ctx.reply('Nie udało się wykonać komendy. Sprawdź logi bota.')


if __name__ == '__main__':
    if not TOKEN or not API_KEY or not CHANNEL_ID:
        raise SystemExit('Uzupełnij DISCORD_TOKEN, YOUTUBE_API_KEY i DISCORD_CHANNEL_ID w .env')
    db().close()
    bot.run(TOKEN)
