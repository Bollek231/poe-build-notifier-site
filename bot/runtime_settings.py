"""Validated, persistent Discord-managed settings (no credentials exposed).

Settings live in the pre-existing SQLite bot_settings table. Validation is
independent from discord.py and prevents dangerous schedules or API budgets.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

PREFIX = 'runtime:'


@dataclass(frozen=True)
class Setting:
    key: str
    kind: str
    minimum: float | None = None
    maximum: float | None = None
    label_pl: str = ''
    label_en: str = ''
    description_pl: str = ''
    description_en: str = ''


SETTINGS: tuple[Setting, ...] = (
    Setting('scan_interval_hours','int',1,24,'Automatyczne skanowanie (h)','Auto scan interval (h)','1–24 godzin','1–24 hours'),
    Setting('digest_time','time',None,None,'Godzina podsumowania','Daily digest time','HH:MM, strefa Warszawa','HH:MM, Warsaw time'),
    Setting('digest_enabled','bool',None,None,'Codzienne podsumowanie','Daily digest','Włącz lub wyłącz','On or off'),
    Setting('results_per_query','int',1,50,'Wyniki na wyszukiwanie','Results per query','1–50 filmów','1–50 videos'),
    Setting('send_delay_seconds','float',1,30,'Odstęp wiadomości (s)','Post delay (s)','1–30 sekund','1–30 seconds'),
    Setting('daily_search_budget','int',1,10000,'Limit zapytań dziennie','Daily search budget','1–10000 zapytań','1–10000 searches'),
    Setting('reserved_searches','int',0,9999,'Rezerwa ręcznych zapytań','Manual-search reserve','Mniej niż dzienny limit','Less than daily budget'),
    Setting('video_age_hours','int',1,24,'Maksymalny wiek filmu (h)','Maximum video age (h)','1–24 godzin (nigdy starsze)','1–24 hours (never older)'),
    Setting('link_refresh_hours','int',1,24,'Odświeżanie przycisków (h)','Link refresh interval (h)','1–24 godzin','1–24 hours'),
    Setting('links_check_enabled','bool',None,None,'Sprawdzanie linków','Check external links','Włącz lub wyłącz','On or off'),
    Setting('version_check_enabled','bool',None,None,'Powiadomienia o wersji','Update notifications','Włącz lub wyłącz','On or off'),
    Setting('version_check_hours','int',1,72,'Sprawdzanie GitHub (h)','GitHub version check (h)','1–72 godzin','1–72 hours'),
    Setting('link_refresh_limit','int',1,50,'Filmy na odświeżenie','Posts per link refresh','1–50','1–50'),
)
SPECS = {item.key: item for item in SETTINGS}


def normalize_language(value: str | None) -> str | None:
    if not isinstance(value,str): return None
    names={'pl':'pl','polski':'pl','polish':'pl','en':'en','english':'en','angielski':'en','eng':'en'}
    return names.get(value.strip().casefold())


def parse_value(key: str, raw: str | int | float | bool):
    """Parse and strictly validate one value, raising ValueError on failure."""
    spec=SPECS.get(key)
    if spec is None: raise ValueError('Setting not editable')
    if spec.kind=='bool':
        if isinstance(raw,bool): return raw
        word=str(raw).strip().lower()
        if word in ('on','true','1','yes','tak','włącz','wlacz'): return True
        if word in ('off','false','0','no','nie','wyłącz','wylacz'): return False
        raise ValueError('Expected on/off or true/false')
    raw_str=str(raw).strip()
    if spec.kind=='time':
        if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',raw_str):
            raise ValueError('Time must be HH:MM in 24-hour format')
        return raw_str
    if spec.kind=='int':
        if not re.fullmatch(r'(?:0|[1-9]\d*)',raw_str):raise ValueError('Expected a whole number')
        value=int(raw_str)
    elif spec.kind=='float':
        if not re.fullmatch(r'(?:0|[1-9]\d*)(?:\.\d{1,2})?',raw_str):
            raise ValueError('Expected a positive number with up to 2 decimals')
        value=float(raw_str)
    else: raise ValueError('Unknown setting type')
    if spec.minimum is not None and value<spec.minimum:raise ValueError(f'Minimum: {spec.minimum:g}')
    if spec.maximum is not None and value>spec.maximum:raise ValueError(f'Maximum: {spec.maximum:g}')
    return value


def serialize(value):
    if isinstance(value,bool):return 'true' if value else 'false'
    return str(value)


def get_language(connection) -> str:
    from storage import get_setting
    return normalize_language(get_setting(connection,'bot_language','pl')) or 'pl'


def set_language(connection, code: str) -> str:
    from storage import set_setting
    code=normalize_language(code)
    if code is None:raise ValueError('Choose Polish or English')
    set_setting(connection,'bot_language',code)
    return code


def snapshot(connection, defaults: dict) -> dict:
    from storage import get_setting
    values={}
    for spec in SETTINGS:
        default=parse_value(spec.key,defaults[spec.key])
        raw=get_setting(connection,PREFIX+spec.key,serialize(default))
        try: values[spec.key]=parse_value(spec.key,raw)
        except ValueError: values[spec.key]=default  # safe fallback for legacy/broken storage
    # A migrated DB or .env may hold inconsistent budgets; prefer safe fallback.
    if values['reserved_searches']>=values['daily_search_budget']:
        values['reserved_searches']=0
    return values


def validate_update(key: str, raw, current: dict) -> dict:
    if key not in SPECS:raise ValueError('Setting not editable')
    new=current.copy()
    new[key]=parse_value(key,raw)
    if new['reserved_searches'] >= new['daily_search_budget']:
        raise ValueError('Manual reserve must be less than daily budget')
    return new


def update_setting(connection, defaults: dict, key: str, raw) -> dict:
    from storage import set_setting
    current=snapshot(connection,defaults)
    changed=validate_update(key,raw,current)
    set_setting(connection,PREFIX+key,serialize(changed[key]))
    return changed


def display_value(key: str, value, lang='pl') -> str:
    if isinstance(value,bool):
        return ('On' if value else 'Off') if lang=='en' else ('Włączone' if value else 'Wyłączone')
    if key=='digest_time':return str(value)+' (Warsaw)'
    return str(value)


def label(key: str, lang='pl') -> str:
    s=SPECS[key]
    return s.label_en if lang=='en' else s.label_pl


def description(key: str, lang='pl') -> str:
    s=SPECS[key]
    return s.description_en if lang=='en' else s.description_pl
