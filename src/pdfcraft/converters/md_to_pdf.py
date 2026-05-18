"""
Convert Markdown files to PDF via HTML intermediate.

Uses WeasyPrint (HTML/CSS -> PDF) with emoji-supporting fonts.
"""

import logging
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "codehilite",
    "toc",
    "nl2br",
    "sane_lists",
]


def _load_stylesheet() -> CSS:
    """Load the default CSS from templates/default.css."""
    css_path = _TEMPLATES_DIR / "default.css"
    return CSS(filename=str(css_path))


def _markdown_to_html(md_text: str) -> str:
    """Render Markdown to a complete HTML document string."""
    body = markdown.markdown(md_text, extensions=MD_EXTENSIONS)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>{body}</body>
</html>"""


def convert_file(md_path: Path, output_dir: Path) -> Path:
    """Convert a single Markdown file to PDF. Returns the output PDF path."""
    logger.info("Converting %s", md_path)
    md_text = md_path.read_text(encoding="utf-8")
    html = _markdown_to_html(md_text)
    stylesheet = _load_stylesheet()

    pdf_path = output_dir / (md_path.stem + ".pdf")
    HTML(string=html, base_url=str(md_path.parent)).write_pdf(
        pdf_path, stylesheets=[stylesheet]
    )
    logger.info("Written %s", pdf_path)
    return pdf_path


def convert_directory(input_dir: Path, output_dir: Path) -> list[Path]:
    """Convert all *.md files in input_dir to PDFs in output_dir."""
    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        logger.warning("No *.md files found in %s", input_dir)
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []

    for md_path in md_files:
        try:
            pdf_path = convert_file(md_path, output_dir)
            results.append(pdf_path)
        except Exception:
            logger.exception("Failed to convert %s", md_path)
            errors.append(md_path)

    logger.info("Done. Converted %d file(s), %d error(s).", len(results), len(errors))
    return results
