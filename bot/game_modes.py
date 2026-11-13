"""Path of Exile 1 / Path of Exile 2 game routing and strict version filters.

No credentials or network requests. PoE 2 targets 1.0 by default ahead of the
announced 2026-12-11 launch. The filter never treats a recently re-uploaded
0.x guide as a 1.0 build simply because its YouTube publish date is recent.
"""
from __future__ import annotations

import re

DEFAULT_GAME = 'poe1'
DEFAULT_POE2_VERSION = '1.0'
POE2_VERSION_REGEX = re.compile(r'(?<!\d)(?:0|[1-9]\d?)[.](?:\d{1,2})(?:[.]\d{1,2})?(?!\d)')
POE2_VERSION_VALID = re.compile(r'[0-9]{1,2}[.]\d{1,2}(?:[.]\d{1,2})?\Z')
GAME2_TOKEN = re.compile(r'(?<![a-z\d])(?:poe[\s-]*2|path\s+of\s+exile\s*(?:2|ii))(?![a-z\d])', re.I)
GAME1_EXPLICIT_TOKEN = re.compile(r'(?<![a-z\d])(?:poe[\s-]*1|path\s+of\s+exile\s*1)(?![a-z\d])', re.I)
GUIDE_TOKEN = re.compile(r'\b(?:build(?:s)?|guide|league\s+starter|starter\s+build|level(?:ing|ling)|endgame|mapping|bossing)\b', re.I)
REJECT_TITLE = re.compile(r'\b(?:trailer|reaction|patch\s*notes|tier\s*list|livestream|podcast|review|interview|reupload|re-upload|outdated|old\s+build|showcase\s+only)\b', re.I)

POE2_QUERY_TEMPLATES = (
    'Path of Exile 2 {version} build guide',
    'PoE2 {version} league starter build',
    'PoE 2 {version} leveling build',
    'Path of Exile 2 {version} endgame build',
    'PoE2 {version} bossing build',
    'PoE 2 {version} starter guide',
    'Path of Exile 2 {version} new class build',
    'PoE2 {version} launch build guide',
)

POE2_ASCENDANCIES = (
    'Titan','Warbringer','Smith of Kitava','Deadeye','Pathfinder',
    'Stormweaver','Chronomancer','Disciple of Varashta',
    'Gemling Legionnaire','Witchhunter','Tactician',
    'Invoker','Acolyte of Chayula','Martial Artist',
    'Blood Mage','Infernalist','Lich','Abyssal Lich',
    'Amazon','Spirit Walker','Ritualist','Shaman','Oracle',
    'Knight','Master-at-Arms','Assassin','Infiltrator',
)

POE2_SKILLS = (
    'Gas Grenade', 'Explosive Grenade', 'Flash Grenade', 'Oil Grenade',
    'Ice Strike', 'Tempest Flurry', 'Skeletal Arsonist', 'Skeletal Sniper',
    'Frost Wall', 'Comet', 'Flameblast', 'Storm Wave', 'Falling Thunder',
    'Spear Throw', 'Rapid Shot', 'Galvanic Shards', 'High Velocity Rounds',
    'Bonestorm', 'Essence Drain', 'Contagion', 'Lightning Arrow',
    'Spark', 'Frostbolt', 'Ice Nova', 'Fireball', 'Poisonburst Arrow',
    'Lightning Rod', 'Tornado', 'Volcanic Fissure', 'Ice Shot',
    'Shield Wall', 'Whirling Assault', 'Sunder', 'Charged Staff',
)


def normalize_game(value: str) -> str | None:
    normalized = value.strip().casefold().replace(' ', '').replace('-', '')
    aliases = {
        'poe1': 'poe1', 'poe': 'poe1', '1': 'poe1', 'pathofexile1': 'poe1',
        'poe2': 'poe2', '2': 'poe2', 'pathofexile2': 'poe2',
    }
    return aliases.get(normalized)


def game_label(game: str) -> str:
    return 'Path of Exile 2' if game == 'poe2' else 'Path of Exile 1'


def valid_poe2_version(value: str) -> bool:
    return bool(POE2_VERSION_VALID.fullmatch(value))


def target_queries(version: str, templates: list[str] | tuple[str, ...] | None = None) -> list[str]:
    if not valid_poe2_version(version):
        raise ValueError('Invalid PoE 2 version')
    result=[]
    for template in templates or POE2_QUERY_TEMPLATES:
        if not isinstance(template,str):
            continue
        clean=template.strip()
        if not clean:continue
        if '{version}' in clean:
            result.append(clean.replace('{version}',version))
        else:
            result.append(f'{clean} PoE 2 {version}')
    return result


def version_in_text(text: str, version: str) -> bool:
    """Accept 1.0, 1.0.0, 1.0.1 for target 1.0, not 1.1 / 0.5."""
    for match in POE2_VERSION_REGEX.finditer(text):
        number=match.group()
        if number == version or number.startswith(version+'.'):
            return True
    return False


def title_has_conflicting_version(title: str, target: str) -> bool:
    return any(not (m.group()==target or m.group().startswith(target+'.'))
               for m in POE2_VERSION_REGEX.finditer(title))


def is_target_poe2_guide(title: str, description: str, version: str='1.0') -> bool:
    """Require evidence of PoE 2 + target 1.0 and a build signal.

    Publication-age filtering happens separately in the caller and remains
    a strict 24-hour window.
    """
    if not valid_poe2_version(version):return False
    if title_has_conflicting_version(title,version):return False
    if GAME1_EXPLICIT_TOKEN.search(title):return False
    if REJECT_TITLE.search(title):return False
    if not GUIDE_TOKEN.search(title):return False
    if not (GAME2_TOKEN.search(title) or GAME2_TOKEN.search(description[:220])):
        return False
    if not (version_in_text(title,version) or version_in_text(description[:380],version)):
        return False
    return True
