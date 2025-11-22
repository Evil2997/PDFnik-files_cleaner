import logging
import time

from main_app.actions.cleanup_dir import cleanup_dir
from main_app.models.cleanup_stats import CleanupStats
from main_app.settings import settings


def run_cleanup_round() -> CleanupStats:
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
