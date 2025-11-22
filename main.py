#!/usr/bin/env python
import logging
import time
from pathlib import Path

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FILES_ROOT: Path = Field(default=Path("/data_files_storage"), alias="FILES_ROOT")
    IMAGES_TTL_HOURS: NonNegativeInt = Field(default=1, alias="IMAGES_TTL_HOURS")
    PDF_TTL_HOURS: NonNegativeInt = Field(default=24, alias="PDF_TTL_HOURS")
    CHECK_INTERVAL_SECONDS: PositiveInt = Field(default=600, alias="CHECK_INTERVAL_SECONDS")

    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    oneshot: bool = Field(default=False, alias="ONESHOT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def images_ttl_seconds(self) -> int:
        return int(self.images_ttl_hours) * 3600

    @property
    def pdf_ttl_seconds(self) -> int:
        return int(self.pdf_ttl_hours) * 3600


class CleanupStats(BaseModel):
    scanned: int = 0
    deleted: int = 0
    errors: int = 0


def setup_logging(level: str) -> None:
    effective_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=effective_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


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


def run_cleanup_round(settings: Settings) -> CleanupStats:
    now = time.time()
    logging.info("Cleanup round started")

    images_dir = settings.FILES_ROOT / "images"
    pdf_dir = settings.FILES_ROOT / "pdf"

    total = CleanupStats()

    img_stats = cleanup_dir(images_dir, settings.IMAGES_TTL_HOURS, now)
    total.scanned += img_stats.scanned
    total.deleted += img_stats.deleted
    total.errors += img_stats.errors

    pdf_stats = cleanup_dir(pdf_dir, settings.PDF_TTL_HOURS, now)
    total.scanned += pdf_stats.scanned
    total.deleted += pdf_stats.deleted
    total.errors += pdf_stats.errors

    logging.info(
        "Cleanup round finished: scanned=%d, deleted=%d, errors=%d",
        total.scanned,
        total.deleted,
        total.errors,
    )

    return total


def main() -> None:
    settings = Settings()
    setup_logging(settings.LOG_LEVEL)

    logging.info("files-cleaner starting with settings: %s", settings)

    try:
        while True:
            run_cleanup_round(settings)
            if settings.oneshot:
                logging.info("ONESHOT mode enabled, exiting after single round")
                break
            time.sleep(settings.CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt, shutting down")


if __name__ == "__main__":
    main()
