"""
Extract text, tables, and image OCR content from a PDF file.

Uses pdfplumber for text and tables, PyMuPDF for image extraction,
and pytesseract for OCR on embedded images.
"""

import io
import logging

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


def _format_table(table: list[list]) -> str:
    """Format a pdfplumber table as pipe-delimited rows."""
    rows = []
    for row in table:
        cells = [str(cell or "").strip() for cell in row]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def _ocr_images_for_page(fitz_page: fitz.Page, page_num: int) -> str:
    """Extract images from a PyMuPDF page and return OCR'd text."""
    doc = fitz_page.parent
    ocr_parts = []

    for img_info in fitz_page.get_images(full=True):
        xref = img_info[0]
        try:
            base_image = doc.extract_image(xref)
            image = Image.open(io.BytesIO(base_image["image"]))
            ocr_text = pytesseract.image_to_string(image).strip()
            if ocr_text:
                ocr_parts.append(ocr_text)
        except Exception:
            logger.debug("Skipped unreadable image on page %d (xref %d)", page_num, xref)

    return "\n".join(ocr_parts)


def extract_pdf_to_text(pdf_path: str) -> str:
    """
    Extract all readable content from a PDF.

    Page text and tables come from pdfplumber; image OCR comes from
    PyMuPDF + pytesseract. Content is assembled page-by-page so context
    is preserved.
    """
    page_sections = []

    fitz_doc = fitz.open(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, plumber_page in enumerate(pdf.pages):
            parts = []

            # Plain text
            text = plumber_page.extract_text()
            if text and text.strip():
                parts.append(text.strip())

            # Tables
            tables = plumber_page.extract_tables()
            for table in tables:
                formatted = _format_table(table)
                if formatted.strip():
                    parts.append(f"[Table]\n{formatted}")

            # Image OCR
            fitz_page = fitz_doc[page_num]
            image_text = _ocr_images_for_page(fitz_page, page_num + 1)
            if image_text:
                parts.append(f"[Image text]\n{image_text}")

            if parts:
                header = f"--- Page {page_num + 1} ---"
                page_sections.append(header + "\n" + "\n\n".join(parts))

    fitz_doc.close()

    if not page_sections:
        logger.warning("No readable content found in %s", pdf_path)
        return ""

    return "\n\n".join(page_sections)
