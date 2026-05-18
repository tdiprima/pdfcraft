"""
Utilities for deriving output paths and writing text files.
"""

import logging
import os

logger = logging.getLogger(__name__)


def derive_output_path(pdf_path: str) -> str:
    """Return the .txt output path derived from the PDF path."""
    base = os.path.splitext(pdf_path)[0]
    return base + ".txt"


def sanitize_filename(name: str, extension: str = ".txt") -> str:
    """Strip unsafe characters and ensure the filename has the right extension."""
    safe = "".join(c for c in name if c.isalnum() or c in "-_.")
    if not safe:
        safe = "summary"
    if not safe.endswith(extension):
        safe += extension
    return safe


def write_text_file(path: str, content: str) -> None:
    """Write a string to a UTF-8 text file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    logger.info("Wrote %d characters to %s", len(content), path)
