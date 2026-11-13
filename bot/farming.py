"""Currency farming strategy discovery for PoE 1 / PoE 2.

Keeps strategy posts separate from builds, respects version and game's strict
filters, and stores no secrets or external price estimates.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import features
import game_modes

TOPICS = {
    "general": ("Ogólne / General", ("currency", "farming", "profit", "divine", "chaos", "money")),
    "atlas": ("Atlas / Mapping", ("atlas", "mapping", "map farming", "map sustain")),
    "essence": ("Essence", ("essence", "essences")),
    "harvest": ("Harvest", ("harvest", "lifeforce")),
    "expedition": ("Expedition", ("expedition", "tujen", "rog", "logbook")),
    "delirium": ("Delirium", ("delirium", "simulacrum")),
    "breach": ("Breach", ("breach", "breachstone")),
    "ritual": ("Ritual", ("ritual",)),
    "legion": ("Legion", ("legion", "timeless splinter")),
    "blight": ("Blight", ("blight", "blighted map")),
    "heist": ("Heist", ("heist", "blueprint", "contract farming")),
    "sanctum": ("Sanctum", ("sanctum",)),
    "bossing": ("Boss farming", ("boss farming", "boss rush", "boss rushing", "invitation farming")),
    "crafting": ("Crafting for profit", ("crafting for profit", "crafting currency", "profit crafting")),
    "trading": ("Trading / Flipping", ("flipping", "trading", "trade strategy")),
}
AUTO_TOPICS = ("general", "atlas", "essence", "harvest", "expedition", "bossing", "crafting", "trading")
ALIASES = {"all": "general", "currency": "general", "maps": "atlas",
           "map": "atlas", "profit": "general", "trade": "trading", "boss": "bossing"}
MONEY = re.compile(
    r"\b(?:farm(?:ing)?|currency|profit(?:able)?|divines?|chaos\s+orbs?|"
    r"money|wealth|loot|flipp?ing|earn(?:ing)?|income|gold\s+farm)\b", re.I)
HOWTO = re.compile(
    r"\b(?:guide|strategy|strategies|method|methods|farm(?:ing)?|profit|"
    r"atlas|setup|how\s+to|currency|money|divines?|loot|flipp?ing)\b", re.I)
REJECT = re.compile(
    r"\b(?:trailer|reaction|patch\s+notes|tier\s+list|livestream|"
    r"podcast|interview|reupload|re-upload|showcase\s+only|giveaway)\b", re.I)
GAME_MARKER = re.compile(r"\b(?:poe(?:\s*1)?|path\s+of\s+exile(?:\s*1)?)\b", re.I)


def normalize_topic(topic: str) -> str | None:
    candidate = topic.strip().casefold()
    if len(candidate) > 30 or not re.fullmatch(r"[a-z0-9 -]+", candidate):
        return None
    candidate = ALIASES.get(candidate, candidate)
    return candidate if candidate in TOPICS else None


def queries(game: str, version: str, topic: str | None = None) -> list[str]:
    """Always include current game and version in the Youtube query."""
    if game not in ("poe1", "poe2"):
        raise ValueError("Unknown game")
    if topic is not None:
        chosen = normalize_topic(topic)
        if chosen is None:
            raise ValueError("Unknown farming topic")
        topics = (chosen,)
    else:
        topics = AUTO_TOPICS
    game_name = "Path of Exile 2" if game == "poe2" else "Path of Exile"
    names = {
        "general": "currency farming guide",
        "atlas": "atlas mapping currency strategy",
        "essence": "essence farming profit strategy",
        "harvest": "harvest currency farming",
        "expedition": "expedition currency farming",
        "delirium": "delirium currency farming",
        "breach": "breach currency farming",
        "ritual": "ritual currency farming",
        "legion": "legion currency farming",
        "blight": "blight currency farming",
        "heist": "heist currency farming",
        "sanctum": "sanctum currency farming",
        "bossing": "boss farming currency strategy",
        "crafting": "crafting for profit",
        "trading": "flipping trading currency guide",
    }
    return [f"{game_name} {version} {names[key]}" for key in topics]


def classify(title: str, description: str, game: str, version: str) -> str | None:
    """Accept current-patch PoE currency strategies, not regular build guides."""
    title = title[:500]
    preview = description[:600]
    lower = title.casefold()
    if REJECT.search(title) or not (MONEY.search(title) and HOWTO.search(title)):
        return None
    # Money signal must be in the title, not a boilerplate channel description.
    if "build" in lower and not any(x in lower for x in ("strategy", "currency", "profit", "atlas", "method")):
        return None
    if game == "poe1":
        if game_modes.GAME2_TOKEN.search(title) or game_modes.GAME2_TOKEN.search(preview[:220]):
            return None
        if features.title_conflicts_with_league(title, version):
            return None
        if not features.mentions_league(title, preview, version):
            return None
        if not GAME_MARKER.search(title + " " + preview[:220]):
            return None
    elif game == "poe2":
        if not game_modes.valid_poe2_version(version):
            return None
        if game_modes.GAME1_EXPLICIT_TOKEN.search(title) or game_modes.title_has_conflicting_version(title, version):
            return None
        if not (game_modes.GAME2_TOKEN.search(title) or game_modes.GAME2_TOKEN.search(preview[:220])):
            return None
        if not (game_modes.version_in_text(title, version) or game_modes.version_in_text(preview[:380], version)):
            return None
    else:
        return None
    for key, (name, words) in TOPICS.items():
        if key == "general":
            continue
        if any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", lower) for w in words):
            return name
    return "Currency farming"


def initialize(c) -> None:
    c.execute("""CREATE TABLE IF NOT EXISTS farm_posts (
        video_id TEXT PRIMARY KEY, game TEXT NOT NULL, version TEXT NOT NULL,
        category TEXT NOT NULL, title TEXT NOT NULL, posted_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS farm_queue (
        video_id TEXT PRIMARY KEY, game TEXT NOT NULL, version TEXT NOT NULL,
        category TEXT NOT NULL, title TEXT NOT NULL, published_at TEXT,
        queued_at TEXT NOT NULL)""")
    c.commit()


def cleanup(c, retention_days=7) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    c.execute("DELETE FROM farm_posts WHERE posted_at < ?", (cutoff,))
    c.execute("DELETE FROM farm_queue WHERE queued_at < ?", (cutoff,))
    c.commit()


def is_queued(c, video_id: str) -> bool:
    return c.execute("SELECT 1 FROM farm_queue WHERE video_id=?", (video_id,)).fetchone() is not None


def queue(c, video_id: str, game: str, version: str, category: str, title: str,
          published_at: str) -> None:
    c.execute("INSERT OR IGNORE INTO farm_queue VALUES (?,?,?,?,?,?,?)",
              (video_id, game, version, category, title, published_at, datetime.now(timezone.utc).isoformat()))
    c.commit()


def queued(c, limit: int = 25):
    return c.execute("SELECT * FROM farm_queue ORDER BY queued_at LIMIT ?", (limit,)).fetchall()


def posted(c, video_id: str, game: str, version: str, category: str, title: str,
           published_at: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    url = "https://www.youtube.com/watch?v=" + video_id
    c.execute("INSERT OR IGNORE INTO videos(video_id,title,url,published_at,sent_at) VALUES (?,?,?,?,?)",
              (video_id, title, url, published_at, now))
    c.execute("INSERT OR IGNORE INTO farm_posts VALUES(?,?,?,?,?,?)",
              (video_id, game, version, category, title, now))
    c.execute("DELETE FROM farm_queue WHERE video_id=?", (video_id,))
    c.commit()


def recent(c, game: str, version: str, limit: int = 10):
    return c.execute("SELECT video_id,title,category FROM farm_posts "
                     "WHERE game=? AND version=? ORDER BY posted_at DESC LIMIT ?",
                     (game, version, limit)).fetchall()
