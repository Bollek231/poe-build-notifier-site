"""Online SQLite backups with retention. No credentials or Discord access."""
from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

POLAND = ZoneInfo('Europe/Warsaw')
BACKUP_PATTERN = re.compile(r'poe-backup-(\d{4}-\d{2}-\d{2})\.sqlite3\Z')


def backup_database(db_path: str | Path, directory: str | Path, *, keep: int = 7,
                    now: datetime | None = None) -> tuple[Path, bool]:
    """Create one consistent SQLite snapshot a day; keep at most `keep` snapshots.

    Does not copy .env / Discord credentials. Never deletes live SQLite database.
    Backup files remain private and should live on a persistent disk.
    """
    if not 1 <= keep <= 30:
        raise ValueError('keep must be from 1 to 30')
    src=Path(db_path).resolve(strict=True)
    if not src.is_file():
        raise ValueError('SQLite database path is not a file')
    dest_dir=Path(directory).resolve()
    if dest_dir == src.parent and src.name.startswith('poe-backup-'):
        raise ValueError('source must be the live database, not a backup')
    dest_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    try:os.chmod(dest_dir,0o700)
    except OSError:pass
    stamp=(now or datetime.now(tz=POLAND)).astimezone(POLAND).date().isoformat()
    dest=dest_dir / f'poe-backup-{stamp}.sqlite3'
    did_create = False
    if not dest.is_file():
        temp=dest_dir / f'.poe-backup-{stamp}-{os.getpid()}.tmp'
        try:
            with sqlite3.connect(str(src),timeout=20) as origin, sqlite3.connect(str(temp),timeout=20) as backup:
                origin.backup(backup)
                result=backup.execute('PRAGMA quick_check').fetchone()
                if result != ('ok',):
                    raise RuntimeError('Backup failed SQLite quick_check')
            try:os.chmod(temp,0o600)
            except OSError:pass
            os.replace(temp,dest)
            did_create=True
        finally:
            temp.unlink(missing_ok=True)
    others=sorted((p for p in dest_dir.iterdir() if p.is_file() and BACKUP_PATTERN.fullmatch(p.name)),reverse=True)
    for extra in others[keep:]:
        extra.unlink()
    return dest,did_create
