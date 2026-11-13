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
import runtime_settings
import localization
import community
import translation_providers
from features import farming

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('poe330')
TOKEN = os.getenv('DISCORD_TOKEN', '').strip()
API_KEY = os.getenv('YOUTUBE_API_KEY', '').strip()
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))
FARM_CHANNEL_ID = int(os.getenv('FARM_CHANNEL_ID', str(CHANNEL_ID))) or CHANNEL_ID
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
TRANSLATION_API_KEY = os.getenv('TRANSLATION_API_KEY','').strip()
TRANSLATION_DAILY_LIMIT = max(1,min(100,int(os.getenv('TRANSLATION_DAILY_LIMIT','30'))))
MYMEMORY_CONTACT_EMAIL = os.getenv('MYMEMORY_CONTACT_EMAIL','').strip()
TRANSLATION_PROVIDER = os.getenv('TRANSLATION_PROVIDER', 'google' if TRANSLATION_API_KEY else 'mymemory').strip().lower()
if TRANSLATION_PROVIDER not in translation_providers.PROVIDERS:
    TRANSLATION_PROVIDER = 'mymemory'
BOT_LANGUAGE = "pl"  # Single configured Discord server / announcement channel
ALERT_CHANNEL_ID = int(os.getenv('ALERT_CHANNEL_ID', str(CHANNEL_ID)))
CHECK_EXTERNAL_LINKS = os.getenv('CHECK_EXTERNAL_LINKS', 'true').lower() in ('true','1','yes','on')
LINK_REFRESH_INTERVAL_HOURS = max(1, int(os.getenv('LINK_REFRESH_INTERVAL_HOURS','6')))
MAX_LINK_REFRESH_PER_RUN = max(1, min(50,int(os.getenv('MAX_LINK_REFRESH_PER_RUN','10'))))
BACKUP_DIR = os.getenv('BACKUP_DIR', str(Path(DB_PATH).parent / 'backups'))
BACKUP_KEEP_DAYS = max(1,min(30,int(os.getenv('BACKUP_KEEP_DAYS','7'))))
VERSION_CHECK_ENABLED = os.getenv('VERSION_CHECK_ENABLED','true').lower() in ('true','1','yes','on')
VERSION_CHECK_INTERVAL_HOURS = max(1,min(72,int(os.getenv('VERSION_CHECK_INTERVAL_HOURS','12'))))
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
        await channel.send(localization.translate(quota_message(reset_at),BOT_LANGUAGE), allowed_mentions=discord.AllowedMentions.none())
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
    community.init(c)
    community.cleanup(c,CACHE_RETENTION_DAYS)
    translation_providers.init(c)
    translation_providers.cleanup(c,CACHE_RETENTION_DAYS)
    farming.initialize(c)
    farming.cleanup(c,CACHE_RETENTION_DAYS)
    storage.cleanup(c, CACHE_RETENTION_DAYS)
    return c


# Editable settings use the original .env as defaults, plus safe SQLite overrides.
SETTING_DEFAULTS = {
    'scan_interval_hours': min(24, INTERVAL_H),
    'digest_time': DAILY_DIGEST_TIME,
    'digest_enabled': DAILY_DIGEST_ENABLED,
    'results_per_query': MAX_RESULTS,
    'send_delay_seconds': max(1., min(30., SEND_DELAY)),
    'daily_search_budget': DAILY_SEARCH_BUDGET,
    'reserved_searches': min(RESERVED_SEARCHES, max(0, DAILY_SEARCH_BUDGET-1)),
    'video_age_hours': min(24, MAX_VIDEO_AGE_HOURS),
    'link_refresh_hours': min(24, LINK_REFRESH_INTERVAL_HOURS),
    'links_check_enabled': CHECK_EXTERNAL_LINKS,
    'version_check_enabled': VERSION_CHECK_ENABLED,
    'version_check_hours': VERSION_CHECK_INTERVAL_HOURS,
    'translation_provider': TRANSLATION_PROVIDER,
    'link_refresh_limit': MAX_LINK_REFRESH_PER_RUN,
}


def language():
    return BOT_LANGUAGE


def localize_embed(embed):
    if BOT_LANGUAGE != 'en':return embed
    if embed.title:embed.title=localization.translate(embed.title,BOT_LANGUAGE)
    if embed.description:embed.description=localization.translate(embed.description,BOT_LANGUAGE)
    for i, field in enumerate(embed.fields):
        embed.set_field_at(i,name=localization.translate(field.name,BOT_LANGUAGE),
            value=localization.translate(field.value,BOT_LANGUAGE),inline=field.inline)
    if embed.footer and embed.footer.text:
        embed.set_footer(text=localization.translate(embed.footer.text,BOT_LANGUAGE))
    return embed


async def localized_reply(ctx, content=None, **kwargs):
    if isinstance(content,str):content=localization.translate(content,BOT_LANGUAGE)
    if kwargs.get('embed') is not None: kwargs['embed']=localize_embed(kwargs['embed'])
    return await ctx.reply(content,**kwargs)


def apply_runtime_values(values: dict):
    """Apply validated settings immediately, including active loop scheduling."""
    global INTERVAL_H,DAILY_DIGEST_TIME,DAILY_DIGEST_ENABLED,MAX_RESULTS,SEND_DELAY
    global DAILY_SEARCH_BUDGET,RESERVED_SEARCHES,MAX_VIDEO_AGE_HOURS
    global LINK_REFRESH_INTERVAL_HOURS,CHECK_EXTERNAL_LINKS,VERSION_CHECK_ENABLED,MAX_LINK_REFRESH_PER_RUN
    global VERSION_CHECK_INTERVAL_HOURS
    INTERVAL_H=values['scan_interval_hours']
    DAILY_DIGEST_TIME=values['digest_time']
    DAILY_DIGEST_ENABLED=values['digest_enabled']
    MAX_RESULTS=values['results_per_query']
    SEND_DELAY=values['send_delay_seconds']
    DAILY_SEARCH_BUDGET=values['daily_search_budget']
    RESERVED_SEARCHES=values['reserved_searches']
    MAX_VIDEO_AGE_HOURS=values['video_age_hours']
    LINK_REFRESH_INTERVAL_HOURS=values['link_refresh_hours']
    CHECK_EXTERNAL_LINKS=values['links_check_enabled']
    VERSION_CHECK_ENABLED=values['version_check_enabled']
    VERSION_CHECK_INTERVAL_HOURS=values['version_check_hours']
    MAX_LINK_REFRESH_PER_RUN=values['link_refresh_limit']
    automatic_scan.change_interval(hours=INTERVAL_H)
    automatic_link_refresh.change_interval(hours=LINK_REFRESH_INTERVAL_HOURS)
    automatic_version_check.change_interval(hours=VERSION_CHECK_INTERVAL_HOURS)


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
            elif host in ('poeplanner.com', 'www.poeplanner.com') and enhancements.sane_external_url(raw):
                found.setdefault('PoE Planner', raw)
        except ValueError:
            continue
    return found


EMBED_STYLES = ('expanded', 'compact')


def notification_embed(*, title, translated, url, game, league, category,
                       channel_title, published, thumbnail=None,
                       content_type='build', skill=None, ascendancy=None,
                       style='expanded', language='pl'):
    """Create Discord-native dark-fantasy notifications; no CSS or HTML.

    Both styles remain within Discord's embed field/title limits. Preserve
    the original YouTube title when automatic translation is enabled.
    """
    if style not in EMBED_STYLES:
        style = 'expanded'
    pl = language != 'en'
    farm = content_type == 'farm'
    accent = discord.Color.from_rgb(237, 176, 49) if farm else discord.Color.from_rgb(170, 93, 235)
    game_label = game_modes.game_label(game)
    safe_title = discord.utils.escape_mentions(str(translated or title)).replace('\n', ' ').strip()[:256]
    heading = safe_title or ('Farming strategy' if farm else 'Build guide')
    embed = discord.Embed(title=heading, url=url, color=accent)
    brand = '💰 FARMING STRATEGY' if farm else '⚔️ BUILD GUIDE'
    embed.set_author(name=f'{brand}  •  {game_label.upper()}  •  {league}'[:256])
    label = (lambda p, e: p if pl else e)
    category = (category or label('Ogólna', 'General'))[:100]
    author = discord.utils.escape_markdown(discord.utils.escape_mentions(str(channel_title or 'YouTube')))[:200]
    published_at = f'<t:{int(published.timestamp())}:R>' if published else label('Nieznana', 'Unknown')
    original = str(title or '').strip()
    original_line = ''
    if translated != title and original:
        original_line = ('\n' + label('**Oryginalny tytuł:** ', '**Original title:** ') +
                         discord.utils.escape_mentions(original[:380]))
    if style == 'compact':
        embed.description = (f'**{label("Kategoria", "Category")}:** {category}  •  '
                             f'**{label("Autor", "Creator")}:** {author}\n'
                             f'🎮 {game_label} · {league}  •  🕒 {published_at}')
        if not farm and skill:
            embed.description += f'\n✨ **{discord.utils.escape_mentions(str(skill)[:90])}**'
        embed.description += original_line
    else:
        embed.description = (
            f'{brand}  **•  {category}**\n'
            + (label('Poradnik strategii zarabiania waluty', 'Currency farming guide') if farm
               else label('Nowy poradnik buildu', 'New build guide'))
            + original_line
        )
        if not farm:
            if skill:
                embed.add_field(name='✨ ' + label('Umiejętność', 'Skill'),
                                value=discord.utils.escape_mentions(str(skill)[:1024]),inline=True)
            if ascendancy:
                embed.add_field(name='🛡️ Ascendancy',
                                value=discord.utils.escape_mentions(str(ascendancy)[:1024]),inline=True)
        embed.add_field(name='🎮 ' + label('Gra', 'Game'),value=game_label,inline=True)
        embed.add_field(name='🏷️ ' + label('Liga / Wersja', 'League / Patch'),value=str(league)[:100],inline=True)
        embed.add_field(name='🗂️ ' + label('Kategoria', 'Category'),value=category,inline=True)
        embed.add_field(name='👤 ' + label('Twórca', 'Creator'),value=author or 'YouTube',inline=True)
        embed.add_field(name='🕒 ' + label('Opublikowano', 'Published'),value=published_at,inline=True)
    embed.set_footer(text=('PoE Build Notifier • YouTube • '
                           + (label('Zyski nie są weryfikowane', 'Earnings are not verified') if farm
                              else label('Oryginalny poradnik', 'Original guide'))))
    if isinstance(thumbnail, str) and thumbnail.startswith('https://'):
        embed.set_thumbnail(url=thumbnail)
    return embed


def buttons_from_links(links, video_id=None):
    if not links and not video_id:
        return None
    view = discord.ui.View(timeout=None)
    if video_id and community.VIDEO_ID.fullmatch(video_id):
        view.add_item(SaveBuildButton(video_id))
        view.add_item(discord.ui.Button(label='YouTube',emoji='▶️',
            style=discord.ButtonStyle.link,url='https://www.youtube.com/watch?v='+video_id))
    # Discord lays out at most five components per row; excess links wrap.
    labels={'Path of Building':'PoB','Maxroll':'Maxroll',
            'Mobalytics':'Mobalytics','PoE Planner':'PoE Planner'}
    for label, url in links.items():
        if not enhancements.sane_external_url(url):
            continue
        view.add_item(discord.ui.Button(label=labels.get(label,label)[:80],
            style=discord.ButtonStyle.link,url=url))
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
        self.add_item(discord.ui.Button(label=localization.choose('Polityka prywatności','Privacy policy',BOT_LANGUAGE), style=discord.ButtonStyle.link, url=PRIVACY_URL))
        self.add_item(discord.ui.Button(label=localization.choose('Warunki korzystania','Terms of use',BOT_LANGUAGE), style=discord.ButtonStyle.link, url=TERMS_URL))

    @discord.ui.button(label='Agree / Akceptuję', style=discord.ButtonStyle.success, custom_id='poe_privacy_accept_20261112')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, answer = await grant_discord_consent(interaction.user, interaction.guild)
        await interaction.response.send_message(localization.translate(answer,BOT_LANGUAGE), ephemeral=True)

    @discord.ui.button(label='Revoke / Cofnij', style=discord.ButtonStyle.secondary, custom_id='poe_privacy_revoke_20261112')
    async def revoke(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, answer = await remove_discord_consent(interaction.user, interaction.guild)
        await interaction.response.send_message(localization.translate(answer,BOT_LANGUAGE), ephemeral=True)


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
        await channel.send(discord.utils.escape_mentions(localization.translate(message[:1700],BOT_LANGUAGE)),allowed_mentions=discord.AllowedMentions.none())
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


async def scan(kind='auto', custom_query=None, *, content_type='build', max_videos=None):
    if scan_lock.locked():
        return None
    if kind=='auto':
        probe=db()
        try:
            if community.pause_until(probe):
                return {'sent':0,'searched':0,'warning':'Skanowanie automatyczne wstrzymane.'}
        finally:probe.close()
    async with scan_lock:
        _health['last_start'] = utc_now().isoformat()
        c = db()
        link_session = None
        try:
            config = cfg()
            game = storage.current_game(c)
            league = storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
            query_pool = (farming.queries(game,league) if content_type=='farm' else
                          game_modes.target_queries(league,config['poe2_search_queries']) if game=='poe2' else
                          features.rendered_queries(config['search_queries'],league))
            queries = [custom_query] if custom_query else query_pool
            pause = storage.quota_pause(c)
            if pause:
                # Official quota is exhausted. No API calls until its PT reset.
                return {'sent': 0, 'searched': 0, 'warning': quota_message(pause[0]), 'quota_exhausted': True}
            destination_id = FARM_CHANNEL_ID if content_type=='farm' else CHANNEL_ID
            channel = bot.get_channel(destination_id) or await bot.fetch_channel(destination_id)
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
                if content_type=='farm':
                    count=min(count,1)  # at most one extra YouTube search each scheduled interval
                cursor_key='query_cursor_'+game+('_farm' if content_type=='farm' else '')
                try:cursor=int(storage.get_setting(c,cursor_key,'0'))
                except ValueError:cursor=0
                queries,next_cursor=enhancements.rotate_queries(queries,min(budget,count),cursor)
                storage.set_setting(c,cursor_key,str(next_cursor))
            else:
                queries=queries[:min(budget,3) if content_type=='farm' and custom_query is None else budget]
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
                    ids = [vid for vid in candidates if not c.execute('SELECT 1 FROM videos WHERE video_id=?', (vid,)).fetchone()
                           and not (content_type=='farm' and farming.is_queued(c,vid))]
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
            queued = 0
            accepted = 0
            link_session=aiohttp.ClientSession()
            # Oldest first. Always verify age locally, even if YouTube search
            # returned a video outside the requested publishedAfter window.
            for vid, info in sorted(candidates.items(), key=lambda it: (
                0 if storage.channel_rule(c,it[1].get('channelId',''))=='allow' else 1,
                it[1].get('publishedAt', ''))):
                if enhancements.scan_limit_reached(accepted, max_videos):
                    break
                published = parse_time(info.get('publishedAt'))
                if published is None or not (utc_now() - timedelta(hours=MAX_VIDEO_AGE_HOURS) <= published <= utc_now() + timedelta(minutes=2)):
                    continue
                if c.execute('SELECT 1 FROM videos WHERE video_id=?', (vid,)).fetchone():
                    continue
                if content_type=='farm' and farming.is_queued(c,vid):
                    continue
                channel_id=info.get('channelId','')
                channel_rule=storage.channel_rule(c,channel_id)
                if channel_rule=='block' or (storage.get_setting(c,'allowlist_only','false')=='true' and channel_rule!='allow'):
                    continue
                title = info.get('title', 'Film YouTube')
                description = info.get('description', '')
                if content_type=='farm':
                    category=farming.classify(title, description, game, league)
                    if category is None:
                        continue
                    skill,asc,fp=None,None,None
                else:
                    result = classify(title, description, config['exclude_phrases'], league, game)
                    if result is None:
                        continue
                    skill, asc, category = result
                    # Existing build filters do not apply to farming strategies.
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
                # Quiet hours do not spend additional API units. Only metadata of
                # accepted fresh videos is queued; a single digest is sent later.
                qstart,qend=community.get_quiet(c)
                if community.is_quiet(utc_now(),qstart,qend):
                    if content_type=='farm':
                        farming.queue(c,vid,game,league,category,title,info.get('publishedAt',''))
                        queued += 1
                        accepted += 1
                    elif community.queue_video(c,vid,game,league,title,info.get('publishedAt','')):
                        queued += 1
                        accepted += 1
                    continue
                url = f'https://www.youtube.com/watch?v={vid}'
                translate_enabled=storage.get_setting(c,'translate_titles','false')=='true'
                translated=title
                if translate_enabled:
                    provider=runtime_settings.snapshot(c,SETTING_DEFAULTS)['translation_provider']
                    translated=await translation_providers.translate_to_english(
                        link_session,c,title,provider=provider,google_api_key=TRANSLATION_API_KEY,
                        contact_email=MYMEMORY_CONTACT_EMAIL,enabled=True,
                        max_daily=TRANSLATION_DAILY_LIMIT,
                        source_language=info.get('defaultLanguage') or info.get('defaultAudioLanguage'))
                thumb = info.get('thumbnails', {}).get('high') or info.get('thumbnails', {}).get('medium') or {}
                embed = notification_embed(
                    title=title, translated=translated, url=url, game=game,
                    league=league, category=category, channel_title=info.get('channelTitle','YouTube'),
                    published=published, thumbnail=thumb.get('url'),
                    content_type=content_type, skill=skill, ascendancy=asc,
                    style=storage.get_setting(c,'embed_style','expanded'),
                    language=BOT_LANGUAGE)
                try:
                    links=extract_links(description)
                    if CHECK_EXTERNAL_LINKS:
                        links=await services.verified_links(link_session,c,links)
                    else:
                        links={label:target for label,target in links.items() if enhancements.sane_external_url(target)}
                    if sent:
                        await asyncio.sleep(SEND_DELAY)
                    posted_message=await channel.send(embed=embed, view=buttons_from_links(links,vid), allowed_mentions=discord.AllowedMentions.none())
                    if content_type=='farm':
                        farming.posted(c,vid,game,league,category,title,info.get('publishedAt'))
                    else:
                        c.execute('INSERT OR IGNORE INTO videos VALUES(?,?,?,?,?)',
                                  (vid, title, url, info.get('publishedAt'), utc_now().isoformat()))
                        c.execute('INSERT OR IGNORE INTO builds(fingerprint,canonical_title,first_video_id,created_at,league) VALUES(?,?,?,?,?)',
                                  (fp, title, vid, utc_now().isoformat(), league))
                        c.execute('INSERT OR REPLACE INTO video_metadata VALUES(?,?,?,?)',
                                  (vid, skill, asc, category))
                        c.commit()
                    # Both notification types can gain new PoB/Maxroll/Mobalytics links.
                    storage.record_post(c,vid,channel.id,posted_message.id,links)
                    sent += 1
                    accepted += 1
                except discord.HTTPException as exc:
                    await notify_error(f'Nie udało się wysłać filmu na Discord: {exc}')
                    break
            result = {'sent': sent, 'queued': queued, 'searched': searched,
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
                embed=localize_embed(embed)
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
    c_quiet=db()
    try:
        quiet_start,quiet_end=community.get_quiet(c_quiet)
        if community.is_quiet(utc_now(),quiet_start,quiet_end):return
    finally:c_quiet.close()
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
        c=db()
        try:
            farm_auto=storage.get_setting(c,'farm_auto','false')=='true'
        finally:
            c.close()
        if farm_auto:
            await scan('auto',content_type='farm')
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
                        await message.edit(view=buttons_from_links(merged,vid))
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


@tasks.loop(hours=VERSION_CHECK_INTERVAL_HOURS)
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
        bot.add_dynamic_items(SaveBuildButton)
        bot._privacy_view_registered = True
    if not automatic_scan.is_running():
        automatic_scan.start()
    if not automatic_digest.is_running():
        automatic_digest.start()
    if not automatic_link_refresh.is_running():
        automatic_link_refresh.start()
    if not automatic_backup.is_running():
        automatic_backup.start()
    if not automatic_version_check.is_running():
        automatic_version_check.start()
    if not automatic_quiet_flush.is_running():
        automatic_quiet_flush.start()


def allowed(ctx):
    return ctx.channel.id == CHANNEL_ID and ctx.guild is not None and ctx.author.guild_permissions.manage_guild


async def require_consent(ctx):
    c = db()
    try:
        agreed = ctx.guild is not None and storage.has_consent(c, ctx.guild.id, ctx.author.id, POLICY_VERSION)
    finally:
        c.close()
    if not agreed:
        await localized_reply(ctx, 'Najpierw zaakceptuj politykę prywatności. Wpisz `pPrivacy`, a następnie kliknij „Akceptuję zasady” lub użyj `pAgree`.')
    return agreed


@bot.command(name='Privacy', aliases=['Zasady'])
@commands.guild_only()
async def privacy_command(ctx):
    await localized_reply(ctx, '**PoE Build Notifier — zgoda i dokumenty**\n'
                    'Bot przetwarza publiczne informacje o filmach z YouTube, a także minimalne informacje o zgodzie na Discordzie. '
                    'Przed korzystaniem z komend administratora zapoznaj się z polityką prywatności i warunkami korzystania. '
                    'Kliknij „Akceptuję zasady”, aby korzystać z komend administracyjnych. Powiadomienia na Discordzie pozostają dostępne na dotychczasowym kanale.',
                    view=ConsentView(), allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Agree', aliases=['Zgoda'])
@commands.guild_only()
async def agree_command(ctx):
    ok, message = await grant_discord_consent(ctx.author, ctx.guild)
    await localized_reply(ctx, message, allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Revoke', aliases=['CofnijZgode'])
@commands.guild_only()
async def revoke_command(ctx):
    ok, message = await remove_discord_consent(ctx.author, ctx.guild)
    await localized_reply(ctx, message, allowed_mentions=discord.AllowedMentions.none())


async def report_scan(ctx, custom=None, *, content_type='build', max_videos=None):
    if scan_lock.locked():
        await localized_reply(ctx, 'Skanowanie już trwa. Poczekaj na jego zakończenie.')
        return
    # Avoid 'search starting' noise if we've already learned Google's quota is exhausted.
    connection = db()
    try:
        pause = storage.quota_pause(connection)
    finally:
        connection.close()
    if pause:
        await localized_reply(ctx, quota_message(pause[0]), allowed_mentions=discord.AllowedMentions.none())
        return
    await localized_reply(ctx, '🔎 Rozpoczynam wyszukiwanie YouTube…')
    try:
        result = await scan('manual', custom, content_type=content_type, max_videos=max_videos)
        if result is None:
            await localized_reply(ctx, 'Skanowanie już trwa.')
        elif result.get('quota_exhausted') or result.get('budget_exhausted'):
            await localized_reply(ctx, result['warning'], allowed_mentions=discord.AllowedMentions.none())
        else:
            await localized_reply(ctx, f"Skan zakończony. Nowe filmy: **{result['sent']}**. "
                            + (f"Do kolejki ciszy: **{result.get('queued',0)}**. " if result.get('queued') else '')
                            + f"Wykonane wyszukiwania: **{result['searched']}**. "
                            + result['warning'])
    except Exception as exc:
        log.exception('Manual scan error')
        await notify_error(f'Ręczne skanowanie: {exc}')
        await localized_reply(ctx, 'Wystąpił błąd skanowania. Sprawdź komunikat bota.')


@bot.command(name='Scan')
@commands.check(allowed)
async def scan_command(ctx, count: str=''):
    if not await require_consent(ctx):
        return
    try:
        max_videos=enhancements.parse_scan_limit(count)
    except ValueError:
        await localized_reply(ctx, 'Użycie: `pScan` albo `pScan LICZBA` (1–25), np. `pScan 1` lub `pScan 2`.')
        return
    await report_scan(ctx,max_videos=max_videos)


@bot.command(name='Search')
@commands.check(allowed)
async def search_command(ctx, *, query: str = ''):
    if not await require_consent(ctx):
        return
    query = query.strip()
    if len(query) < 3 or len(query) > 100:
        await localized_reply(ctx, 'Użycie: `pSearch Lightning Strike Slayer` (3–100 znaków).')
        return
    c = db()
    try:
        game=storage.current_game(c)
        league=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
    finally:
        c.close()
    label = 'PoE 2' if game=='poe2' else 'PoE'
    await report_scan(ctx, f'{label} {league} {query} build')


@bot.command(name='EmbedStyle')
@commands.check(allowed)
async def embed_style_command(ctx, mode: str='status'):
    """Persist a compact or expanded layout for new build/farming notifications."""
    if not await require_consent(ctx):
        return
    mode=mode.strip().casefold()
    if mode not in (*EMBED_STYLES,'status'):
        await localized_reply(ctx, localization.choose(
            'Użycie: `pEmbedStyle compact`, `pEmbedStyle expanded` lub `pEmbedStyle status`.',
            'Usage: `pEmbedStyle compact`, `pEmbedStyle expanded`, or `pEmbedStyle status`.',
            BOT_LANGUAGE))
        return
    c=db()
    try:
        if mode != 'status':
            storage.set_setting(c,'embed_style',mode)
        selected=storage.get_setting(c,'embed_style','expanded')
    finally:
        c.close()
    await localized_reply(ctx, localization.choose(
        f'🎨 Styl nowych powiadomień: **{selected}**. Nowy układ dotyczy tylko przyszłych wiadomości.',
        f'🎨 New notification style: **{selected}**. Existing messages stay unchanged.',
        BOT_LANGUAGE))


@bot.command(name='FarmScan')
@commands.check(allowed)
async def farm_scan_command(ctx, count: str=''):
    """Search farming strategies (up to three queries), optionally cap new videos."""
    if not await require_consent(ctx):
        return
    try:
        max_videos=enhancements.parse_scan_limit(count)
    except ValueError:
        await localized_reply(ctx, 'Użycie: `pFarmScan` albo `pFarmScan LICZBA` (1–25), np. `pFarmScan 1`.')
        return
    await report_scan(ctx,content_type='farm',max_videos=max_videos)


@bot.command(name='FarmSearch')
@commands.check(allowed)
async def farm_search_command(ctx, *, topic: str='general'):
    if not await require_consent(ctx):
        return
    normalized=farming.normalize_topic(topic)
    if normalized is None:
        await localized_reply(ctx, 'Nieznana kategoria. Użyj `pFarmTopics` (np. `pFarmSearch essence`).')
        return
    c=db()
    try:
        game=storage.current_game(c)
        version=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
    finally:
        c.close()
    query=farming.queries(game,version,normalized)[0]
    await report_scan(ctx,query,content_type='farm')


@bot.command(name='FarmAuto')
@commands.check(allowed)
async def farm_auto_command(ctx, mode: str='status'):
    if not await require_consent(ctx):
        return
    c=db()
    try:
        mode=mode.strip().lower()
        if mode in ('on','off'):
            storage.set_setting(c,'farm_auto','true' if mode=='on' else 'false')
        enabled=storage.get_setting(c,'farm_auto','false')=='true'
    finally:
        c.close()
    if mode not in ('status','on','off'):
        await localized_reply(ctx,'Użycie: `pFarmAuto on`, `pFarmAuto off` lub `pFarmAuto status`.')
        return
    await localized_reply(ctx, ('💰 Automatyczne wyszukiwanie strategii: **włączone**.' if enabled else
                                '💰 Automatyczne wyszukiwanie strategii: **wyłączone**.') +
                           ' Maksymalnie 1 dodatkowe zapytanie YouTube na interwał, współdzielony budżet API.')


@bot.command(name='FarmTopics')
@commands.guild_only()
async def farm_topics_command(ctx):
    if ctx.channel.id!=CHANNEL_ID:
        return
    rows=[f'`{key}` — {label}' for key,(label,_) in farming.TOPICS.items()]
    await localized_reply(ctx,'💰 **Kategorie strategii / Farming topics**\n'+
                          '\n'.join(rows)+'\nPrzykład: `pFarmSearch essence`.',
                          mention_author=False)


@bot.command(name='FarmRecent')
@commands.guild_only()
async def farm_recent_command(ctx):
    if ctx.channel.id!=CHANNEL_ID:
        return
    c=db()
    try:
        game=storage.current_game(c)
        version=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        rows=farming.recent(c,game,version)
    finally:
        c.close()
    if not rows:
        await localized_reply(ctx,'Brak znalezionych strategii farmienia dla wybranej wersji gry.')
        return
    lines=[f'{i}. [{discord.utils.escape_markdown(row["title"][:80])}](https://youtu.be/{row["video_id"]}) — {row["category"]}'
           for i,row in enumerate(rows,1)]
    await localized_reply(ctx,'💰 **Strategie farmienia / Farming strategies**\n'+'\n'.join(lines),
                          allowed_mentions=discord.AllowedMentions.none())


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
            await localized_reply(ctx, '📊 **YouTube API**\n' + quota_message(pause[0]) +
                            '\nLokalny licznik: **' + str(searches) + '** wyszukiwań; '
                            'nie jest oficjalnym odczytem Google.',
                            allowed_mentions=discord.AllowedMentions.none())
            return
        await localized_reply(ctx, 
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
    await localized_reply(ctx, '🩺 **Stan bota v'+VERSION+'**\n'
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
            await localized_reply(ctx, 'Brak zapisanych buildów.')
            return
        lines = [f'{i}. {discord.utils.escape_mentions(r["canonical_title"][:100])} — https://youtu.be/{r["first_video_id"]}'
                 for i, r in enumerate(rows, 1)]
        await localized_reply(ctx, f'**Ostatnie buildy (historia w bazie z ostatnich {CACHE_RETENTION_DAYS} dni):**\n' + '\n'.join(lines), allowed_mentions=discord.AllowedMentions.none())
    finally:
        c.close()


def settings_embed(values, lang=None):
    lang=lang or BOT_LANGUAGE
    title=localization.choose('⚙️ Ustawienia PoE Build Notifier','⚙️ PoE Build Notifier settings',lang)
    subtitle=localization.choose('Wybierz parametr z menu, aby go zmienić. Zmiany zapisują się automatycznie i działają bez restartu.',
                                'Choose an option below to edit it. Changes are saved automatically and take effect without a restart.',lang)
    embed=discord.Embed(title=title,description=subtitle,color=discord.Color.dark_purple())
    for key in runtime_settings.SPECS:
        embed.add_field(name=runtime_settings.label(key,lang),
            value=runtime_settings.display_value(key,values[key],lang),inline=True)
    embed.set_footer(text=localization.choose('Bezpieczne zakresy • Tylko administrator • SQLite • Nie zmienia tokenów ani ID kanałów',
            'Validated ranges • Admin only • SQLite • No token or channel-ID edits',lang))
    return embed


async def setting_interaction_allowed(interaction,owner_id,guild_id):
    if (interaction.user.id!=owner_id or interaction.guild_id!=guild_id
        or interaction.channel_id!=CHANNEL_ID
        or not interaction.user.guild_permissions.manage_guild):
        await interaction.response.send_message(
            localization.choose('Tylko administrator, który otworzył menu, może używać tych przycisków.',
                                'Only the administrator who opened this menu can use it.',BOT_LANGUAGE),ephemeral=True)
        return False
    c=db()
    try:authorized=storage.has_consent(c,guild_id,owner_id,POLICY_VERSION)
    finally:c.close()
    if not authorized:
        await interaction.response.send_message(
            localization.choose('Najpierw zaakceptuj zasady przez pAgree.',
                                'Accept the terms using pAgree first.',BOT_LANGUAGE),ephemeral=True)
    return authorized


class SettingsModal(discord.ui.Modal):
    def __init__(self,view,key):
        self.settings_view=view
        self.key=key
        self.lang=BOT_LANGUAGE
        super().__init__(title=runtime_settings.label(key,self.lang)[:45],timeout=180)
        c=db()
        try:values=runtime_settings.snapshot(c,SETTING_DEFAULTS)
        finally:c.close()
        self.setting_input=discord.ui.TextInput(label=runtime_settings.label(key,self.lang)[:45],
            placeholder=runtime_settings.description(key,self.lang)[:100],
            default=str(values[key]),max_length=20,min_length=1,required=True)
        self.add_item(self.setting_input)

    async def on_submit(self,interaction):
        if not await setting_interaction_allowed(interaction,self.settings_view.owner_id,self.settings_view.guild_id):return
        c=db()
        try:
            try:values=runtime_settings.update_setting(c,SETTING_DEFAULTS,self.key,str(self.setting_input.value))
            except ValueError as exc:
                await interaction.response.send_message(
                    localization.choose('Niepoprawna wartość: ','Invalid value: ',BOT_LANGUAGE)+str(exc),ephemeral=True)
                return
        finally:c.close()
        apply_runtime_values(values)
        if self.settings_view.message:
            try:await self.settings_view.message.edit(embed=settings_embed(values),view=self.settings_view)
            except discord.HTTPException:pass
        await interaction.response.send_message(
            localization.choose('✅ Zapisano ustawienie: ','✅ Saved setting: ',BOT_LANGUAGE)
            +f'**{runtime_settings.label(self.key,BOT_LANGUAGE)}** → `{runtime_settings.display_value(self.key,values[self.key],BOT_LANGUAGE)}`',
            ephemeral=True)


class SettingsView(discord.ui.View):
    def __init__(self,owner_id,guild_id):
        super().__init__(timeout=300)
        self.owner_id,self.guild_id=owner_id,guild_id
        self.message=None
        self.add_item(SettingsSelect(self))

    async def interaction_check(self,interaction):
        return await setting_interaction_allowed(interaction,self.owner_id,self.guild_id)

    async def on_timeout(self):
        for item in self.children:item.disabled=True
        if self.message:
            try:await self.message.edit(view=self)
            except discord.HTTPException:pass


class SettingsSelect(discord.ui.Select):
    def __init__(self,view):
        self.settings_view=view
        lang=BOT_LANGUAGE
        options=[discord.SelectOption(label=runtime_settings.label(x.key,lang)[:100],
            value=x.key,description=runtime_settings.description(x.key,lang)[:100])
            for x in runtime_settings.SETTINGS]
        super().__init__(placeholder=localization.choose('Wybierz ustawienie do zmiany','Select a setting to edit',lang),
                         min_values=1,max_values=1,options=options)

    async def callback(self,interaction):
        key=self.values[0]
        spec=runtime_settings.SPECS[key]
        if spec.kind!='bool':
            await interaction.response.send_modal(SettingsModal(self.settings_view,key))
            return
        c=db()
        try:
            current=runtime_settings.snapshot(c,SETTING_DEFAULTS)
            values=runtime_settings.update_setting(c,SETTING_DEFAULTS,key,not current[key])
        finally:c.close()
        apply_runtime_values(values)
        await interaction.response.send_message(
            localization.choose('✅ Zmieniono: ','✅ Updated: ',BOT_LANGUAGE)+
            f'**{runtime_settings.label(key,BOT_LANGUAGE)}** → {runtime_settings.display_value(key,values[key],BOT_LANGUAGE)}',
            ephemeral=True)
        if self.settings_view.message:
            try:await self.settings_view.message.edit(embed=settings_embed(values),view=self.settings_view)
            except discord.HTTPException:pass


class LanguageView(discord.ui.View):
    def __init__(self,owner_id,guild_id):
        super().__init__(timeout=300)
        self.owner_id,self.guild_id=owner_id,guild_id
        self.message=None
        self.add_item(LanguageSelect(self))

    async def interaction_check(self,interaction):
        return await setting_interaction_allowed(interaction,self.owner_id,self.guild_id)

    async def on_timeout(self):
        for item in self.children:item.disabled=True
        if self.message:
            try:await self.message.edit(view=self)
            except discord.HTTPException:pass


class LanguageSelect(discord.ui.Select):
    def __init__(self,view):
        self.language_view=view
        super().__init__(placeholder=localization.choose('Wybierz język bota','Choose bot language',BOT_LANGUAGE),
            options=[discord.SelectOption(label='Polski',value='pl',emoji='🇵🇱'),
                     discord.SelectOption(label='English',value='en',emoji='🇬🇧')],min_values=1,max_values=1)

    async def callback(self,interaction):
        global BOT_LANGUAGE
        c=db()
        try:BOT_LANGUAGE=runtime_settings.set_language(c,self.values[0])
        finally:c.close()
        new_lang=BOT_LANGUAGE
        await interaction.response.send_message(
            localization.choose('✅ Język bota: **polski**. Ustawienie zostało zapisane.',
                                '✅ Bot language: **English**. Setting saved.',new_lang),ephemeral=True)
        if self.language_view.message:
            try:await self.language_view.message.edit(
                content=localization.choose('🌐 **Język bota**: Polski. Aby zmienić, otwórz menu ponownie przez `pLanguage`.',
                                             '🌐 **Bot language**: English. To change it, open the menu again with `pLanguage`.',new_lang),view=None)
            except discord.HTTPException:pass


@bot.command(name='Language',aliases=['Jezyk','Język'])
@commands.check(allowed)
async def language_command(ctx, *, selected: str=''):
    global BOT_LANGUAGE
    if not await require_consent(ctx):return
    if selected:
        choice=runtime_settings.normalize_language(selected)
        if not choice:
            await localized_reply(ctx,localization.choose('Wybierz `pLanguage pl` lub `pLanguage en`, albo wpisz samo `pLanguage`.',
                              'Use `pLanguage pl` or `pLanguage en`, or type `pLanguage` for the menu.',BOT_LANGUAGE))
            return
        c=db()
        try:BOT_LANGUAGE=runtime_settings.set_language(c,choice)
        finally:c.close()
        await localized_reply(ctx,localization.choose('✅ Język bota został zmieniony na **polski**.',
                                                  '✅ Bot language has been set to **English**.',BOT_LANGUAGE))
        return
    view=LanguageView(ctx.author.id,ctx.guild.id)
    message=await localized_reply(ctx,
        localization.choose('🌐 **Wybierz język bota** — polski lub angielski. Wybrany język dotyczy powiadomień i komend na tym serwerze.',
                            '🌐 **Choose bot language** — Polish or English. This changes bot notifications and commands on this server.',BOT_LANGUAGE),view=view)
    view.message=message


@bot.command(name='Settings')
@commands.check(allowed)
async def settings_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:values=runtime_settings.snapshot(c,SETTING_DEFAULTS)
    finally:c.close()
    view=SettingsView(ctx.author.id,ctx.guild.id)
    message=await localized_reply(ctx,embed=settings_embed(values),view=view)
    view.message=message



# Community features — v0.6.2. Command permissions are explicit per feature.
class SaveBuildButton(discord.ui.DynamicItem[discord.ui.Button],
                      template=r'save:(?P<video_id>[A-Za-z0-9_-]{11})'):
    def __init__(self, video_id):
        self.video_id=video_id
        super().__init__(discord.ui.Button(label='⭐ Save / Zapisz',
            style=discord.ButtonStyle.secondary,custom_id='save:'+video_id))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match.group('video_id'))

    async def callback(self,interaction):
        if not interaction.guild or interaction.channel_id not in (CHANNEL_ID, FARM_CHANNEL_ID):
            await interaction.response.send_message('Use the configured bot channel.',ephemeral=True)
            return
        c=db()
        try:
            try:saved=community.saved_toggle(c,interaction.user.id,self.video_id)
            except ValueError as e:
                await interaction.response.send_message(str(e),ephemeral=True)
                return
        finally:c.close()
        msg=('⭐ Zapisano. Lista: `pSaved`.' if saved else 'Usunięto z zapisanych buildów.') if BOT_LANGUAGE=='pl' else (
            '⭐ Saved. List: `pSaved`.' if saved else 'Removed from your saved builds.')
        await interaction.response.send_message(msg,ephemeral=True)


@bot.command(name='Saved')
@commands.guild_only()
async def saved_command(ctx, action='', video_id=''):
    if ctx.channel.id!=CHANNEL_ID:return
    c=db()
    try:
        if action.lower()=='clear':
            count=community.saved_remove(c,ctx.author.id)
            msg=f'Usunięto {count} zakładek.' if BOT_LANGUAGE=='pl' else f'Removed {count} bookmarks.'
        elif action.lower()=='remove':
            if not community.VIDEO_ID.fullmatch(video_id):
                msg='Użycie: `pSaved remove VIDEO_ID`.' if BOT_LANGUAGE=='pl' else 'Usage: `pSaved remove VIDEO_ID`.'
            else:
                count=community.saved_remove(c,ctx.author.id,video_id)
                msg='Usunięto zakładkę.' if count else 'Nie znaleziono zakładki.'
        elif action:
            msg='Użycie: `pSaved`, `pSaved remove VIDEO_ID`, `pSaved clear`.'
        else:
            ids=community.saved_list(c,ctx.author.id)
            msg=('⭐ **Twoje zapisane buildy:**\n' if BOT_LANGUAGE=='pl' else '⭐ **Your saved builds:**\n')+(
                '\n'.join(f'{i}. https://youtu.be/{v}' for i,v in enumerate(ids,1)) if ids else ('Brak zakładek.' if BOT_LANGUAGE=='pl' else 'No bookmarks.'))
    finally:c.close()
    # Prefix commands cannot use ephemeral messages: send user bookmarks via DM.
    try:
        await ctx.author.send(msg,allowed_mentions=discord.AllowedMentions.none())
        await ctx.reply('📩 Sprawdź wiadomość prywatną / Check your DMs.',mention_author=False,delete_after=20)
    except discord.Forbidden:
        await ctx.reply('Nie mogę wysłać DM. Włącz wiadomości prywatne. / Please enable DMs.',mention_author=False,delete_after=30)


HELP_PAGES={
 'scan':('🔎 Wyszukiwanie / Discovery', '`pScan` / `pScan 1` — pełny skan / limit nowych filmów\n`pSearch Spark` — wyszukiwanie skilla\n`pGame poe2` / `pGame poe1` — wybór gry\n`pLeague` — wersja gry\n`pFarmScan` / `pFarmScan 2`, `pFarmSearch essence` — farmienie'),
 'config':('⚙️ Konfiguracja / Settings', '`pSetup` — kreator\n`pSettings` — panel ustawień\n`pLanguage` — język bota\n`pQuietHours 23:00 08:00` — godziny ciszy\n`pPause 6h` / `pResume` — pauza\n`pFarmAuto on/off` — monitoring farmienia\n`pEmbedStyle compact/expanded` — wygląd powiadomień'),
 'community':('⭐ Społeczność / Community','`pSaved` — zapisane buildy\n`pTrending` — popularność filmów\n`pFarmRecent`, `pFarmTopics` — strategie farmienia\n`pTranslateTitles on/off/mymemory/google` — tłumaczenie tytułów'),
 'admin':('🛠️ Administracja / Admin', '`pHealth`, `pLimit`, `pVersion` — stan i API\n`pBackup` — kopie danych\n`pFilters`, `pChannelRules` — reguły\n`pPrivacy` / `pAgree` — zasady')}


class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder='Wybierz kategorię / Select category',
            options=[discord.SelectOption(label=v[0][:90],value=k) for k,v in HELP_PAGES.items()])
    async def callback(self,interaction):
        heading,content=HELP_PAGES[self.values[0]]
        await interaction.response.edit_message(embed=discord.Embed(title=heading,description=content,color=discord.Color.dark_purple()))


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpSelect())


@bot.command(name='Help')
@commands.guild_only()
async def help_command(ctx):
    if ctx.channel.id!=CHANNEL_ID:return
    await ctx.reply(embed=discord.Embed(title='📚 PoE Build Notifier — Help / Pomoc',
        description='Wybierz kategorię z menu poniżej. / Choose a category below.',
        color=discord.Color.dark_purple()),view=HelpView(),mention_author=False)


class SetupSelect(discord.ui.Select):
    def __init__(self,owner,kind):
        self.owner,self.kind=owner,kind
        if kind=='game':opts=[('Path of Exile 1','poe1'),('Path of Exile 2','poe2')]
        elif kind=='language':opts=[('Polski','pl'),('English','en')]
        else:opts=[(f'Co {v} h / Every {v} h',str(v)) for v in (1,2,3,4,6,12,24)]
        super().__init__(placeholder={'game':'Gra / Game','language':'Język / Language','hours':'Skanowanie / Scan interval'}[kind],
            options=[discord.SelectOption(label=l,value=v) for l,v in opts],row={'game':0,'language':1,'hours':2}[kind])
    async def callback(self,interaction):
        self.owner.values[self.kind]=self.values[0]
        if self.kind=='game':
            c=db()
            try:
                self.owner.values['patch']=storage.current_game_version(c,self.values[0],
                    poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
            finally:c.close()
        await interaction.response.edit_message(embed=self.owner.embed(),view=self.owner)


class SetupPatchModal(discord.ui.Modal):
    def __init__(self,owner):
        super().__init__(title='Liga / Wersja gry',timeout=180)
        self.owner=owner
        self.patch=discord.ui.TextInput(label='Patch / Liga',default=owner.values['patch'],max_length=12)
        self.add_item(self.patch)

    async def on_submit(self,interaction):
        if not await setting_interaction_allowed(interaction,self.owner.owner_id,self.owner.guild_id):return
        candidate=str(self.patch.value).strip()
        game=self.owner.values['game']
        okay=game_modes.valid_poe2_version(candidate) if game=='poe2' else features.league_valid(candidate)
        if not okay:
            await interaction.response.send_message('Niepoprawna wersja gry. / Invalid game patch.',ephemeral=True)
            return
        self.owner.values['patch']=candidate
        await interaction.response.edit_message(embed=self.owner.embed(),view=self.owner)


class SetupView(discord.ui.View):
    def __init__(self,owner_id,guild_id,game,language_code,hours,patch):
        super().__init__(timeout=300)
        self.owner_id,self.guild_id=owner_id,guild_id
        self.values={'game':game,'language':language_code,'hours':str(hours),'patch':patch}
        for k in ('game','language','hours'):self.add_item(SetupSelect(self,k))

    async def interaction_check(self,interaction):
        return await setting_interaction_allowed(interaction,self.owner_id,self.guild_id)

    def embed(self):
        return discord.Embed(title='🧭 PoE Build Notifier — pSetup',description=(
            'Wybierz grę, język i interwał. Zmiany zostaną zapisane **dopiero po kliknięciu Zapisz**.\n'
            'Choose game, language and scan interval, then press Save.\n\n'
            f'🎮 **{self.values["game"]}** · 🏷️ **{self.values["patch"]}** · 🌐 **{self.values["language"]}** · ⏱️ **{self.values["hours"]} h**\n'
            'Wersję gry można zmienić później przez `pLeague`; pozostałe parametry przez `pSettings`.'),
            color=discord.Color.dark_purple())

    @discord.ui.button(label='🏷️ Wersja / Patch',style=discord.ButtonStyle.secondary,row=3)
    async def version_button(self,interaction,button):
        await interaction.response.send_modal(SetupPatchModal(self))

    @discord.ui.button(label='✅ Zapisz / Save',style=discord.ButtonStyle.success,row=4)
    async def confirm(self,interaction,button):
        global BOT_LANGUAGE
        c=db()
        try:
            if scan_lock.locked():
                await interaction.response.send_message('Trwa skanowanie. Spróbuj po zakończeniu.',ephemeral=True)
                return
            game=self.values['game'];patch=self.values['patch']
            good=game_modes.valid_poe2_version(patch) if game=='poe2' else features.league_valid(patch)
            if not good:
                await interaction.response.send_message('Niepoprawna wersja gry.',ephemeral=True)
                return
            new=runtime_settings.update_setting(c,SETTING_DEFAULTS,'scan_interval_hours',self.values['hours'])
            storage.set_game_version(c,game,patch)
            storage.set_game(c,game)
            BOT_LANGUAGE=runtime_settings.set_language(c,self.values['language'])
        finally:c.close()
        apply_runtime_values(new)
        for child in self.children:child.disabled=True
        await interaction.response.edit_message(embed=self.embed(),view=self)


@bot.command(name='Setup')
@commands.check(allowed)
async def setup_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:
        game=storage.current_game(c)
        patch=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
    finally:c.close()
    view=SetupView(ctx.author.id,ctx.guild.id,game,BOT_LANGUAGE,INTERVAL_H,patch)
    await localized_reply(ctx,embed=view.embed(),view=view)


@bot.command(name='QuietHours')
@commands.check(allowed)
async def quiet_hours_command(ctx,start='',end=''):
    if not await require_consent(ctx):return
    c=db()
    try:
        if start.lower()=='off':
            community.set_quiet(c)
            text='✅ Godziny ciszy wyłączone. / Quiet hours disabled.'
        elif not start and not end:
            a,b=community.get_quiet(c)
            text=f'🌙 Godziny ciszy: **{a}–{b}** (Warszawa).' if a else '🌙 Godziny ciszy wyłączone / Quiet hours off.'
        else:
            try:
                a,b=community.validate_quiet(start,end)
                community.set_quiet(c,a,b)
                text=f'🌙 Godziny ciszy: **{a}–{b}** (Europe/Warsaw). Bot nadal skanuje, wysyła jedno podsumowanie po ciszy.'
            except ValueError:
                text='Użycie / Usage: `pQuietHours 23:00 08:00`, `pQuietHours off`.'
    finally:c.close()
    await localized_reply(ctx,text)


@bot.command(name='Pause')
@commands.check(allowed)
async def pause_command(ctx, duration='status'):
    if not await require_consent(ctx):return
    c=db()
    try:
        if duration=='status':
            until=community.pause_until(c)
            text=('⏸️ Automatyczne skanowanie działa.' if until is None else
                '⏸️ Wstrzymano bezterminowo.' if until=='forever' else f'⏸️ Pauza do <t:{int(until.timestamp())}:F>.')
        else:
            try:
                until=community.set_pause(c,duration)
                text='⏸️ Wstrzymano automatyczne wyszukiwania. `pResume` wznawia.'
                if until!='forever':text+=' Do <t:'+str(int(datetime.fromisoformat(until).timestamp()))+'>.'
            except ValueError:text='Użycie: `pPause 1h`, `pPause 6h`, `pPause 24h`, `pPause forever`, `pResume`.'
    finally:c.close()
    await localized_reply(ctx,text)


@bot.command(name='Resume')
@commands.check(allowed)
async def resume_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:community.clear_pause(c)
    finally:c.close()
    await localized_reply(ctx,'▶️ Automatyczne skanowanie wznowione. / Automatic scans resumed.')


@bot.command(name='TranslateTitles')
@commands.check(allowed)
async def translate_titles_command(ctx,mode='status',provider_name=''):
    if not await require_consent(ctx):return
    mode=mode.strip().lower()
    provider_name=provider_name.strip().lower()
    c=db()
    try:
        values=runtime_settings.snapshot(c,SETTING_DEFAULTS)
        provider=values['translation_provider']
        if mode in ('mymemory','google'):
            provider_name=mode
            mode='provider'
            auto_enable=True
        else:auto_enable=False
        if mode=='provider':
            if provider_name not in translation_providers.PROVIDERS:
                reply='Użycie: `pTranslateTitles provider mymemory` lub `pTranslateTitles provider google`.'
            elif provider_name=='google' and not TRANSLATION_API_KEY:
                reply='⚠️ Najpierw dodaj prywatny `TRANSLATION_API_KEY` w `.env`, potem wybierz Google.'
            else:
                runtime_settings.update_setting(c,SETTING_DEFAULTS,'translation_provider',provider_name)
                if auto_enable:storage.set_setting(c,'translate_titles','true')
                reply=('✅ Dostawca tłumaczeń: **MyMemory** (bez klucza API).'
                       if provider_name=='mymemory' else
                       '✅ Dostawca tłumaczeń: **Google Cloud Translation**.')
                if auto_enable:reply+=' Tłumaczenie włączone.'
        elif mode=='on':
            if provider=='google' and not TRANSLATION_API_KEY:
                reply='⚠️ Google wymaga `TRANSLATION_API_KEY`. Możesz wybrać bezpłatne `pTranslateTitles mymemory`.'
            else:
                storage.set_setting(c,'translate_titles','true')
                reply=f'✅ Włączono tłumaczenie tytułów na angielski przez **{provider}**.'
        elif mode=='off':
            storage.set_setting(c,'translate_titles','false')
            reply='✅ Tłumaczenie tytułów wyłączone.'
        elif mode=='status':
            enabled=storage.get_setting(c,'translate_titles','false')=='true'
            service='MyMemory (bez klucza API)' if provider=='mymemory' else 'Google Cloud Translation'
            ready=provider=='mymemory' or bool(TRANSLATION_API_KEY)
            reply=(f'🌐 Tłumaczenie: **{"włączone" if enabled else "wyłączone"}**. '
                   f'Dostawca: **{service}**. Konfiguracja: **{"gotowa" if ready else "brakuje klucza Google"}**. '
                   f'Limit bota: **{TRANSLATION_DAILY_LIMIT} zapytań/24h**. '
                   'Zmiana: `pTranslateTitles mymemory` / `pTranslateTitles google` '
                   'lub `pTranslateTitles provider mymemory|google`.')
        else:
            reply=('Użycie: `pTranslateTitles on/off/status`, `pTranslateTitles mymemory`, '
                   '`pTranslateTitles google`, `pTranslateTitles provider mymemory|google`.')
    finally:c.close()
    await localized_reply(ctx,reply)

async def fetch_video_views(session,ids):
    """One videos.list request per 50 IDs; never execute a new search.list."""
    data={}
    for start in range(0,len(ids),50):
        params={'key':API_KEY,'part':'statistics','id':','.join(ids[start:start+50])}
        async with session.get('https://www.googleapis.com/youtube/v3/videos',params=params,
            timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status!=200:raise RuntimeError(f'YouTube statistics HTTP {resp.status}')
            payload=await resp.json(content_type=None)
            for item in payload.get('items',[]):
                try:data[item['id']]=int(item.get('statistics',{}).get('viewCount',-1))
                except (ValueError,TypeError):pass
    return {vid:v for vid,v in data.items() if v>=0}


@bot.command(name='Trending')
@commands.guild_only()
async def trending_command(ctx):
    if ctx.channel.id!=CHANNEL_ID:return
    c=db()
    try:
        game=storage.current_game(c)
        league=storage.current_game_version(c,game,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        cutoff=(utc_now()-timedelta(hours=48)).isoformat()
        rows=c.execute('SELECT v.video_id,v.title FROM videos v JOIN builds b ON b.first_video_id=v.video_id WHERE b.league=? AND v.sent_at>=? ORDER BY v.sent_at DESC LIMIT 30',(league,cutoff)).fetchall()
        ids=[r['video_id'] for r in rows if community.VIDEO_ID.fullmatch(r['video_id'])]
        if not ids:
            await ctx.reply('Brak świeżych buildów do rankingu. / No recent builds for trending.',mention_author=False)
            return
        # Prevent repeated API charges for impatient command invocations.
        recent=c.execute('SELECT MAX(observed_at) FROM video_trends WHERE video_id=?',(ids[0],)).fetchone()[0]
        fresh=recent and datetime.fromisoformat(recent)>utc_now()-timedelta(minutes=15)
        if fresh:
            counts={vid:c.execute('SELECT view_count FROM video_trends WHERE video_id=? ORDER BY observed_at DESC LIMIT 1',(vid,)).fetchone() for vid in ids}
            counts={vid:int(r[0]) for vid,r in counts.items() if r}
            observed=datetime.fromisoformat(recent)
        else:
            async with aiohttp.ClientSession() as session:
                counts=await fetch_video_views(session,ids)
            observed=utc_now()
            for _ in range((len(ids)+49)//50):
                c.execute('INSERT INTO api_usage(used_at,units,operation) VALUES(?,?,?)',(observed.isoformat(),1,'videos.list'))
            c.commit()
        ranked=community.trend_rank(c,counts,observed)
        if not fresh:community.record_views(c,counts,observed)
        names={r['video_id']:r['title'] for r in rows}
        lines=[]
        for i,(vid,rate,growth,views,has_delta) in enumerate(ranked[:8],1):
            title=discord.utils.escape_markdown(names[vid][:65])
            if has_delta:metric=f'+{growth:,} views · {rate:.0f}/h'
            else:metric=f'{views:,} views · collecting baseline'
            lines.append(f'{i}. [{title}](https://youtu.be/{vid}) — {metric}')
        description='\n'.join(lines) if lines else 'Brak danych / No statistics.'
        embed=discord.Embed(title=f'📈 Trending — {game_modes.game_label(game)} {league}',
            description=description,color=discord.Color.dark_purple())
        embed.set_footer(text='YouTube public view counts · sample-based · no search.list calls')
        await ctx.reply(embed=embed,mention_author=False,allowed_mentions=discord.AllowedMentions.none())
    except Exception as exc:
        log.warning('Trending unavailable: %s',type(exc).__name__)
        await ctx.reply('Nie można teraz pobrać statystyk YouTube. / YouTube statistics unavailable.',mention_author=False)
    finally:c.close()


@tasks.loop(minutes=1)
async def automatic_quiet_flush():
    if scan_lock.locked():return
    c=db()
    try:
        start,end=community.get_quiet(c)
        if community.is_quiet(utc_now(),start,end):return
        rows=community.queued(c,limit=25)
        if rows:
            # Keep original build digest semantics; no deleted Discord messages.
            valid=[r for r in rows if community.VIDEO_ID.fullmatch(r['video_id'])]
            lines=[f'• [{discord.utils.escape_markdown(r["title"][:85])}](https://youtu.be/{r["video_id"]}) · {r["game"]} {r["league"]}' for r in valid]
            if lines:
                msg=discord.Embed(title='🌙 Buildy z godzin ciszy / Quiet-hours digest',
                    description='\n'.join(lines)[:3900],color=discord.Color.dark_purple())
                channel=bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)
                await channel.send(embed=msg,allowed_mentions=discord.AllowedMentions.none())
            community.finish_queue(c,rows)
        strategies=farming.queued(c,limit=25)
        if strategies:
            valid=[r for r in strategies if community.VIDEO_ID.fullmatch(r['video_id'])]
            lines=[f'• [{discord.utils.escape_markdown(r["title"][:85])}](https://youtu.be/{r["video_id"]}) · {r["category"]} · {r["game"]} {r["version"]}' for r in valid]
            if lines:
                msg=discord.Embed(title='💰 Strategie z godzin ciszy / Farming digest',
                    description='\n'.join(lines)[:3900],color=discord.Color.gold())
                channel=bot.get_channel(FARM_CHANNEL_ID) or await bot.fetch_channel(FARM_CHANNEL_ID)
                await channel.send(embed=msg,allowed_mentions=discord.AllowedMentions.none())
                for row in valid:
                    farming.posted(c,row['video_id'],row['game'],row['version'],row['category'],
                                   row['title'],row['published_at'])
    except Exception:
        log.exception('Quiet hours queue delivery failed, will retry')
    finally:c.close()


@automatic_quiet_flush.before_loop
async def quiet_flush_wait_ready():
    await bot.wait_until_ready()


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
            await localized_reply(ctx, f'🎮 Gra: **{game_modes.game_label(game)}**, wersja **{version}**.\n'
                            'Przełącz: `pGame poe2` lub `pGame poe1`.')
            return
        new=game_modes.normalize_game(selected)
        if new is None:
            await localized_reply(ctx, 'Użycie: `pGame poe1` lub `pGame poe2`.')
            return
        if scan_lock.locked():
            await localized_reply(ctx, 'Skanowanie trwa. Zmień grę po zakończeniu bieżącego skanu.')
            return
        if game==new:
            await localized_reply(ctx, f'🎮 **{game_modes.game_label(game)} {version}** jest już aktywne.')
            return
        storage.set_game(c,new)
        new_version=storage.current_game_version(c,new,poe1_default=DEFAULT_LEAGUE,poe2_default=DEFAULT_POE2_VERSION)
        await localized_reply(ctx, f'✅ Przełączono grę na **{game_modes.game_label(new)} {new_version}**.\n'
                        'Od teraz `pScan`, `pSearch`, automatyczne skanowanie i podsumowanie używają tej gry. '
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
            await localized_reply(ctx, f'Gra: **{game_modes.game_label(game)}**. Aktualna wersja: **{current}**. '
                            f'Zmiana: `pLeague {sample}`.')
            return
        valid=game_modes.valid_poe2_version(new) if game=='poe2' else features.league_valid(new)
        if not valid:
            await localized_reply(ctx, f'Niepoprawny numer wersji dla {game_modes.game_label(game)}. '
                            f'Użyj np. `pLeague {sample}`.')
            return
        if scan_lock.locked():
            await localized_reply(ctx, 'Skanowanie trwa. Zmień wersję po jego zakończeniu.')
            return
        if new==current:
            await localized_reply(ctx, f'Wersja **{new}** jest już aktywna.')
            return
        storage.set_game_version(c,game,new)
        await localized_reply(ctx, f'✅ {game_modes.game_label(game)}: wersja **{current}** → **{new}**.\n'
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
        await localized_reply(ctx, message or 'Podsumowanie zostało wysłane.', allowed_mentions=discord.AllowedMentions.none())
    except Exception:
        log.exception('Ręczne podsumowanie nie powiodło się')
        await localized_reply(ctx, 'Nie udało się wysłać podsumowania. Sprawdź logi bota.')


@bot.command(name='BlockChannel')
@commands.check(allowed)
async def block_channel_command(ctx, *, channel: str=''):
    if not await require_consent(ctx):return
    ident=enhancements.youtube_channel_id(channel)
    if not ident:
        await localized_reply(ctx, 'Podaj ID kanału YouTube: `pBlockChannel UCxxxxxxxxxxxxxxxxxxxxxx` (lub jego URL /channel/UC...).')
        return
    c=db()
    try:storage.put_channel_rule(c,ident,'block')
    finally:c.close()
    await localized_reply(ctx, f'⛔ Zablokowano kanał YouTube `{ident}`. Nie będzie publikowany.')


@bot.command(name='AllowChannel')
@commands.check(allowed)
async def allow_channel_command(ctx, *, channel: str=''):
    if not await require_consent(ctx):return
    ident=enhancements.youtube_channel_id(channel)
    if not ident:
        await localized_reply(ctx, 'Podaj ID kanału YouTube: `pAllowChannel UCxxxxxxxxxxxxxxxxxxxxxx`.')
        return
    c=db()
    try:storage.put_channel_rule(c,ident,'allow')
    finally:c.close()
    await localized_reply(ctx, f'✅ Zaufany kanał `{ident}`. Priorytet kolejności, ale wszystkie filtry nadal obowiązują.')


@bot.command(name='UnlistChannel')
@commands.check(allowed)
async def unlist_channel_command(ctx, *, channel: str=''):
    if not await require_consent(ctx):return
    ident=enhancements.youtube_channel_id(channel)
    if not ident:
        await localized_reply(ctx, 'Użycie: `pUnlistChannel UCxxxxxxxxxxxxxxxxxxxxxx`.')
        return
    c=db()
    try:removed=storage.delete_channel_rule(c,ident)
    finally:c.close()
    await localized_reply(ctx, 'Usunięto regułę kanału.' if removed else 'Kanału nie było na żadnej liście.')


@bot.command(name='Whitelist')
@commands.check(allowed)
async def whitelist_command(ctx, mode: str=''):
    if not await require_consent(ctx):return
    c=db()
    try:
        if mode.casefold() in ('on','only'):
            if not any(r[1]=='allow' for r in storage.all_channel_rules(c)):
                await localized_reply(ctx, 'Najpierw dodaj zaufany kanał: `pAllowChannel UC...`.')
                return
            storage.set_setting(c,'allowlist_only','true')
        elif mode.casefold()=='off':
            storage.set_setting(c,'allowlist_only','false')
        elif mode:
            await localized_reply(ctx, 'Użycie: `pWhitelist on` (publikuj tylko zaufane kanały) lub `pWhitelist off`.')
            return
        value=storage.get_setting(c,'allowlist_only','false')=='true'
    finally:c.close()
    await localized_reply(ctx, '✅ Biała lista: **tylko zaufane kanały**.' if value else
                    'ℹ️ Biała lista: **priorytet zaufanych, pozostałe dozwolone** (poza zablokowanymi).')


@bot.command(name='ChannelRules')
@commands.check(allowed)
async def channel_rules_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:rules=storage.all_channel_rules(c)
    finally:c.close()
    lines=[f'{"✅ zaufany" if r[1]=="allow" else "⛔ zablokowany"}: `{r[0]}`' for r in rules[:35]]
    await localized_reply(ctx, '📃 **Lista kanałów YouTube**\n'+('\n'.join(lines) if lines else 'Brak reguł.') +
                    ('\n… i kolejne.' if len(rules)>35 else ''),allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Filters')
@commands.check(allowed)
async def filters_command(ctx):
    if not await require_consent(ctx):return
    c=db()
    try:f=storage.get_filters(c,storage.current_game(c))
    finally:c.close()
    values=', '.join(f'**{k}**: `{v}`' for k,v in f.items()) or 'brak (wszystkie zgodne buildy)'
    await localized_reply(ctx, '🎯 **Filtry buildów**\n'+values+'\nPrzykłady: `pFilter skill Lightning Strike`, '
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
        await localized_reply(ctx, '✅ Wyczyszczono wszystkie rozszerzone filtry.')
        return
    c=db()
    try:active_game=storage.current_game(c)
    finally:c.close()
    available_skills=SKILLS+list(game_modes.POE2_SKILLS) if active_game=='poe2' else SKILLS
    available_asc=ASCENDANCIES+list(game_modes.POE2_ASCENDANCIES) if active_game=='poe2' else ASCENDANCIES
    try:canonical=enhancements.validate_filter(field,value,available_skills,available_asc)
    except ValueError:
        await localized_reply(ctx, 'Wybierz: `skill`, `ascendancy`, `class`, `mode` (SSF/HC/SC), '
                        '`stage` (starter/endgame/leveling/build). Wpisz `all`, by usunąć wybrany filtr.')
        return
    c=db()
    try:
        all_filters=storage.get_filters(c,active_game)
        if canonical is None:all_filters.pop(field,None)
        else:all_filters[field]=canonical
        storage.set_filters(c,all_filters,active_game)
    finally:c.close()
    await localized_reply(ctx, f'✅ Filtr `{field}`: `{canonical or "wszystkie"}`. Zmiana obowiązuje przy następnym skanie.')


@bot.command(name='RefreshLinks')
@commands.check(allowed)
async def refresh_links_command(ctx):
    if not await require_consent(ctx):return
    await localized_reply(ctx, '🔗 Sprawdzam linki w ostatnio opublikowanych filmach…')
    try:reply=await refresh_post_links(manual=True)
    except Exception as exc:
        log.exception('Manual refresh error')
        reply=f'Nie udało się odświeżyć przycisków ({type(exc).__name__}).'
    await localized_reply(ctx, reply,allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='Backup')
@commands.check(allowed)
async def backup_command(ctx):
    if not await require_consent(ctx):return
    try:
        path,created=await asyncio.to_thread(backups.backup_database,DB_PATH,BACKUP_DIR,
                                             keep=BACKUP_KEEP_DAYS,now=utc_now())
        await localized_reply(ctx, '💾 **Kopia SQLite**: '+('utworzona' if created else 'już istnieje dzisiaj')+
                        f'. Folder: `{discord.utils.escape_mentions(str(path.parent))}`. '
                        'Plik nie jest publikowany na GitHubie.')
    except Exception as exc:
        log.exception('Manual backup error')
        await localized_reply(ctx, f'Błąd kopii zapasowej ({type(exc).__name__}). Sprawdź logi.')


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
    await localized_reply(ctx, f'📦 **PoE Build Notifier v{VERSION}**\n{status}\n'
                    '📋 https://bollek231.github.io/poe-build-notifier-site/changelog.html\n'
                    'Automatyczne aktualizacje są dostępne przez launcher Windows.',allowed_mentions=discord.AllowedMentions.none())


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return  # Ignore unauthorized command invocations.
    if isinstance(error, commands.CommandNotFound):
        return
    log.error('Command error: %s', error)
    await localized_reply(ctx, 'Nie udało się wykonać komendy. Sprawdź logi bota.')


if __name__ == '__main__':
    if not TOKEN or not API_KEY or not CHANNEL_ID:
        raise SystemExit('Uzupełnij DISCORD_TOKEN, YOUTUBE_API_KEY i DISCORD_CHANNEL_ID w .env')
    c=db()
    try:
        BOT_LANGUAGE=runtime_settings.get_language(c)
        apply_runtime_values(runtime_settings.snapshot(c,SETTING_DEFAULTS))
    finally:c.close()
    bot.run(TOKEN)
