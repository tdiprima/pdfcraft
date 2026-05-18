"""
Logging configuration for pdfcraft.
"""

import logging
import os


def configure_logging(verbose: bool = False) -> None:
    """Configure root logger. Level overridable via LOG_LEVEL env var."""
    env_level = os.environ.get("LOG_LEVEL", "").upper()
    if env_level:
        level = getattr(logging, env_level, logging.INFO)
    else:
        level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=level,
    )
