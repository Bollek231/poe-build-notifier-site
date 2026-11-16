"""Online SQLite backups with retention. No credentials or Discord access."""
from __future__ import annotations

import os
import re
import sqlite3
import tempfile
import time
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

POLAND = ZoneInfo('Europe/Warsaw')
BACKUP_PATTERN = re.compile(r'poe-backup-(\d{4}-\d{2}-\d{2})\.sqlite3\Z')


def _publish_snapshot(source: Path, destination: Path) -> None:
    """Rename a fully closed SQLite snapshot; tolerate short Windows file locks."""
    # Antivirus/file indexers can temporarily hold a finished snapshot on Windows.
    # Do not mask unrelated errors or retry indefinitely.
    for delay in (0.0, 0.15, 0.4, 0.8):
        if delay:
            time.sleep(delay)
        try:
            os.replace(source, destination)
            return
        except PermissionError as exc:
            if getattr(exc, 'winerror', None) != 32 or delay == 0.8:
                raise


def backup_database(db_path: str | Path, directory: str | Path, *, keep: int = 7,
                    now: datetime | None = None) -> tuple[Path, bool]:
    """Create one consistent SQLite snapshot a day; keep at most `keep` snapshots.

    Use the sqlite3 online backup API and CLOSE both connections explicitly.
    sqlite3.Connection as a context manager commits/rolls back, but does not
    close handles. Leaving the temp connection open causes WinError 32 when
    replacing the temporary backup on Windows.

    Never copies .env/Discord credentials or deletes the live database.
    """
    if not 1 <= keep <= 30:
        raise ValueError('keep must be from 1 to 30')
    src = Path(db_path).resolve(strict=True)
    if not src.is_file():
        raise ValueError('SQLite database path is not a file')
    dest_dir = Path(directory).resolve()
    if dest_dir == src.parent and src.name.startswith('poe-backup-'):
        raise ValueError('source must be the live database, not a backup')
    dest_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(dest_dir, 0o700)
    except OSError:
        pass

    stamp = (now or datetime.now(tz=POLAND)).astimezone(POLAND).date().isoformat()
    dest = dest_dir / f'poe-backup-{stamp}.sqlite3'
    did_create = False
    if not dest.is_file():
        # Unique, already-closed temporary file: concurrent manual/automatic
        # snapshots never open the same path.
        fd, temp_name = tempfile.mkstemp(prefix=f'.poe-backup-{stamp}-',
                                         suffix='.tmp', dir=dest_dir)
        os.close(fd)
        temp = Path(temp_name)
        try:
            # contextlib.closing is intentional: "with sqlite3.connect(...)" alone
            # does NOT close the database file descriptor on Windows.
            with closing(sqlite3.connect(str(src), timeout=20)) as origin:
                with closing(sqlite3.connect(str(temp), timeout=20)) as backup:
                    origin.backup(backup)
                    result = backup.execute('PRAGMA quick_check').fetchone()
                    if result != ('ok',):
                        raise RuntimeError('Backup failed SQLite quick_check')
                    backup.commit()
            try:
                os.chmod(temp, 0o600)
            except OSError:
                pass
            if not dest.is_file():
                _publish_snapshot(temp, dest)
                did_create = True
        finally:
            # Remove only our temporary snapshot; never touch an existing backup.
            try:
                temp.unlink(missing_ok=True)
            except PermissionError:
                # A transient external lock must not hide the original error.
                pass

    others = sorted((p for p in dest_dir.iterdir()
                     if p.is_file() and BACKUP_PATTERN.fullmatch(p.name)),
                    reverse=True)
    for extra in others[keep:]:
        extra.unlink()
    return dest, did_create
