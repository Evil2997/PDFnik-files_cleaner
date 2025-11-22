import logging


def setup_logging(level: str) -> None:
    effective_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=effective_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
