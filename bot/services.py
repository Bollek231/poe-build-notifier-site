"""Bounded remote checks for PoE Build Notifier v0.5.1.

Never sends tokens to third-party websites. External links are checked only on
explicitly allowed domains; redirects are not followed.
"""
from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

import aiohttp
from enhancements import sane_external_url

log=logging.getLogger('poe330.services')


async def check_guide_link(session: aiohttp.ClientSession, url: str) -> str:
    """Return ok/dead/uncertain. Do not reject transient failures or bot protections.

    HEAD is used to avoid downloading content. Hosts are strictly allowlisted.
    No redirects are followed (prevents redirection to internal/private hosts).
    """
    if not sane_external_url(url):
        return 'dead'
    try:
        async with session.head(url, timeout=aiohttp.ClientTimeout(total=6),allow_redirects=False) as r:
            if r.status in (404,410):return 'dead'
            if 200 <= r.status < 300:return 'ok'
            if r.status in (405,501):
                # HEAD not supported: use GET and close after receiving headers.
                async with session.get(url,headers={'Range':'bytes=0-0'},timeout=aiohttp.ClientTimeout(total=6),allow_redirects=False) as rr:
                    if rr.status in (404,410):return 'dead'
                    if 200 <= rr.status < 300:return 'ok'
            return 'uncertain'
    except (aiohttp.ClientError,asyncio.TimeoutError,ValueError,OSError) as exc:
        log.info('Could not confirm guide URL availability (%s): %s',type(exc).__name__,urlparse(url).hostname)
        return 'uncertain'


async def verified_links(session: aiohttp.ClientSession, connection, links: dict) -> dict:
    """Keep HTTP 403 / timeout as uncertain to avoid false-negative removal."""
    import storage
    results={}
    for label,url in links.items():
        cached=storage.cached_link_state(connection,url)
        state=cached if cached is not None else await check_guide_link(session,url)
        if cached is None:storage.store_link_state(connection,url,state)
        if state!='dead':results[label]=url
    return results


async def latest_public_version(session: aiohttp.ClientSession, *, url: str =
    'https://raw.githubusercontent.com/Bollek231/poe-build-notifier-site/main/VERSION') -> str | None:
    """Fetch plain public VERSION file, never read credentials or run remote code."""
    from enhancements import parse_version
    try:
        async with session.get(url,timeout=aiohttp.ClientTimeout(total=10),allow_redirects=False) as r:
            if r.status!=200:return None
            if int(r.headers.get('Content-Length','0'))>100:return None
            text=(await r.text())[:100].strip()
            return text if parse_version(text) else None
    except (aiohttp.ClientError,asyncio.TimeoutError,ValueError):
        return None
