import logging
import time

from main_app.actions.run_cleanup_round import run_cleanup_round
from main_app.settings import settings
from main_app.setup_logging import setup_logging


def main() -> None:
    setup_logging(settings.LOG_LEVEL)

    logging.info("files-cleaner starting with settings: %s", settings)

    try:
        while True:
            run_cleanup_round()
            if settings.oneshot:
                logging.info("ONESHOT mode enabled, exiting after single round")
                break
            time.sleep(settings.CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt, shutting down")


if __name__ == "__main__":
    main()
