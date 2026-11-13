"""Independent helpers for v0.6.1. No credentials, network calls or Discord imports."""
from __future__ import annotations

import ipaddress
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

VERSION = '0.6.1'
PACIFIC = ZoneInfo('America/Los_Angeles')
POLAND = ZoneInfo('Europe/Warsaw')
CHANNEL_ID_RE = re.compile(r'UC[A-Za-z0-9_-]{22}\Z')
VALID_CLASS = ('Marauder','Duelist','Ranger','Shadow','Witch','Templar','Scion','Warrior','Sorceress','Mercenary','Monk','Huntress','Druid')
ASC_TO_CLASS = {
    'Slayer':'Duelist','Gladiator':'Duelist','Champion':'Duelist',
    'Juggernaut':'Marauder','Berserker':'Marauder','Chieftain':'Marauder',
    'Deadeye':'Ranger','Raider':'Ranger','Pathfinder':'Ranger','Warden':'Ranger',
    'Assassin':'Shadow','Saboteur':'Shadow','Trickster':'Shadow',
    'Necromancer':'Witch','Occultist':'Witch','Elementalist':'Witch',
    'Inquisitor':'Templar','Hierophant':'Templar','Guardian':'Templar',
    'Ascendant':'Scion',
    # Path of Exile 2 ascendancies; class labels are game-specific.
    'Titan':'Warrior','Warbringer':'Warrior','Smith of Kitava':'Warrior',
    'Stormweaver':'Sorceress','Chronomancer':'Sorceress','Disciple of Varashta':'Sorceress',
    'Gemling Legionnaire':'Mercenary','Witchhunter':'Mercenary','Tactician':'Mercenary',
    'Invoker':'Monk','Acolyte of Chayula':'Monk','Martial Artist':'Monk',
    'Blood Mage':'Witch','Infernalist':'Witch','Lich':'Witch','Abyssal Lich':'Witch',
    'Amazon':'Huntress','Spirit Walker':'Huntress','Ritualist':'Huntress',
    'Shaman':'Druid','Oracle':'Druid','Knight':'Duelist','Master-at-Arms':'Duelist',
    'Infiltrator':'Shadow',
}
ALLOWED_FILTERS = ('skill','ascendancy','class','mode','stage')


def youtube_channel_id(raw: str) -> str | None:
    text = raw.strip().strip('<>')
    if CHANNEL_ID_RE.fullmatch(text):
        return text
    try:
        parsed = urlparse(text)
        if parsed.scheme not in ('https','http') or (parsed.hostname or '').lower() not in ('youtube.com','www.youtube.com','m.youtube.com'):
            return None
        parts = [p for p in parsed.path.split('/') if p]
        if len(parts) == 2 and parts[0] == 'channel' and CHANNEL_ID_RE.fullmatch(parts[1]):
            return parts[1]
    except ValueError:
        pass
    return None


def auto_query_allocation(remaining_total: int, reserve: int, now: datetime, interval_hours: int, query_count: int) -> int:
    """Fairly distribute today's remaining automatic search calls across future scans.

    Manual searches retain the protected reserve; auto never goes past it.
    This local estimate is NOT the official Google Cloud quota.
    """
    usable = max(0, remaining_total - max(0,reserve))
    if usable <= 0 or query_count <= 0:
        return 0
    local = now.astimezone(PACIFIC)
    tomorrow = datetime.combine(local.date()+timedelta(days=1), datetime.min.time(),tzinfo=PACIFIC)
    seconds = max(0.0, (tomorrow.astimezone(timezone.utc) - local.astimezone(timezone.utc)).total_seconds())
    slots = max(1, int((seconds + max(1,interval_hours)*3600 - 1)//(max(1,interval_hours)*3600)))
    # Allow 1 search when budget is short; rotate which query is selected.
    per_scan = max(1, (usable + slots - 1)//slots)
    return min(query_count, usable, per_scan)


def rotate_queries(queries: list[str], allocation: int, cursor: int) -> tuple[list[str], int]:
    if not queries or allocation <= 0:
        return [], cursor
    count = min(len(queries), allocation)
    start = cursor % len(queries)
    return [queries[(start+i)%len(queries)] for i in range(count)], (start+count)%len(queries)


def normalize_filters(filters: dict) -> dict:
    clean={}
    for key in ALLOWED_FILTERS:
        val=str(filters.get(key,'')).strip()
        if val:
            clean[key]=val
    return clean


def validate_filter(key: str, value: str, available_skills: list[str], available_asc: list[str]) -> str | None:
    """Return canonical filter or None. Empty/'all' clears a filter."""
    value=value.strip()
    if value.casefold() in ('','all','clear','any','off'):
        return None
    candidates={
        'skill':available_skills,
        'ascendancy':available_asc,
        'class':VALID_CLASS,
        'mode':('SSF','HC','SC'),
        'stage':('starter','endgame','leveling','build'),
    }.get(key)
    if candidates is None:
        raise ValueError('Unknown filter field')
    for candidate in candidates:
        if value.casefold()==candidate.casefold():
            return candidate
    raise ValueError(f'Incorrect {key} value')


def matches_filters(title: str, description: str, skill: str | None, asc: str | None, stage: str, filters: dict) -> bool:
    f=normalize_filters(filters)
    if not f:return True
    if f.get('skill') and (not skill or skill.casefold()!=f['skill'].casefold()):return False
    if f.get('ascendancy') and (not asc or asc.casefold()!=f['ascendancy'].casefold()):return False
    if f.get('class') and (not asc or ASC_TO_CLASS.get(asc,'').casefold()!=f['class'].casefold()):return False
    if f.get('stage') and stage.casefold() != {'starter':'league starter','endgame':'endgame','leveling':'leveling','build':'build'}[f['stage'].casefold()]:return False
    if f.get('mode'):
        # Only explicit evidence; absence of 'HC' does NOT imply Softcore.
        sample=(title+' '+description[:400]).casefold()
        tokens={
            'ssf':r'\b(?:ssf|solo[ -]?self[ -]?found)\b',
            'hc':r'\b(?:hc|hardcore)\b',
            'sc':r'\b(?:sc|softcore)\b',
        }
        if not re.search(tokens[f['mode'].casefold()],sample):return False
    return True


def links_changed(previous: dict, fresh: dict) -> bool:
    """Add or update known link buttons, never strip buttons when descriptions change."""
    return any(label not in previous or previous[label]!=url for label,url in fresh.items())


def merged_links(previous: dict, fresh: dict) -> dict:
    out=dict(previous)
    out.update(fresh)
    return {k:out[k] for k in ('Path of Building','Maxroll','Mobalytics') if k in out}


def sane_external_url(url: str, known_urls: dict | None = None) -> bool:
    """Restrict probes to exact known third-party guide domains to avoid SSRF."""
    try:
        p=urlparse(url)
        if p.scheme != 'https' or p.username or p.password or p.port not in (None,443) or not p.hostname:
            return False
        host=p.hostname.casefold().rstrip('.')
        if host not in {'pobb.in','www.pobb.in','pastebin.com','www.pastebin.com','poe.ninja','www.poe.ninja','pathofbuilding.community','www.pathofbuilding.community','maxroll.gg','www.maxroll.gg','mobalytics.gg','www.mobalytics.gg'} and not host.endswith('.pathofbuilding.community'):
            return False
        if len(url)>1800 or any(ord(c)<32 for c in url):return False
        try:
            ipaddress.ip_address(host)
            return False
        except ValueError:
            pass
        return True
    except (ValueError,TypeError):
        return False


def parse_version(value: str) -> tuple[int,int,int] | None:
    match=re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)',value.strip())
    return tuple(map(int,match.groups())) if match else None


def is_newer(remote: str, local: str=VERSION) -> bool:
    a,b=parse_version(remote),parse_version(local)
    return a is not None and b is not None and a>b
