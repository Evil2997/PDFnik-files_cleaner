import logging
from pathlib import Path

from main_app.models.cleanup_stats import CleanupStats


def cleanup_dir(path: Path, ttl_seconds: int, now: float) -> CleanupStats:
    stats = CleanupStats()

    if not path.exists():
        logging.warning("Directory does not exist, skipping: %s", path)
        return stats

    if not path.is_dir():
        logging.warning("Path is not a directory, skipping: %s", path)
        return stats

    for entry in path.rglob("*"):
        if entry.is_dir():
            continue

        stats.scanned += 1

        try:
            mtime = entry.stat().st_mtime
        except OSError as e:
            stats.errors += 1
            logging.warning("Failed to stat file %s: %s", entry, e)
            continue

        age = now - mtime
        if age <= ttl_seconds:
            continue

        try:
            entry.unlink()
            stats.deleted += 1
            logging.debug(
                "Deleted file %s (age=%.0f sec, ttl=%d sec)",
                entry,
                age,
                ttl_seconds,
            )
        except OSError as e:
            stats.errors += 1
            logging.error("Failed to delete file %s: %s", entry, e)

    return stats
