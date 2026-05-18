"""
Input validation helpers for pdfcraft CLI commands.
"""

import sys
from pathlib import Path


def require_file(path: str) -> Path:
    """Validate path exists and is a file. Exits with error if not."""
    resolved = Path(path).resolve()
    if not resolved.is_file():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    return resolved


def require_directory(path: str) -> Path:
    """Validate path exists and is a directory. Exits with error if not."""
    resolved = Path(path).resolve()
    if not resolved.is_dir():
        print(f"ERROR: Not a directory: {path}", file=sys.stderr)
        sys.exit(1)
    return resolved
