"""Tests for the md-to-pdf converter."""

import pytest
from pathlib import Path


def test_markdown_to_html_contains_body():
    from pdfcraft.converters.md_to_pdf import _markdown_to_html

    html = _markdown_to_html("# Hello\n\nWorld")
    assert "<h1>" in html
    assert "Hello" in html
    assert "<body>" in html


def test_markdown_to_html_table():
    from pdfcraft.converters.md_to_pdf import _markdown_to_html

    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    html = _markdown_to_html(md)
    assert "<table>" in html


def test_convert_directory_no_md_files(tmp_path):
    from pdfcraft.converters.md_to_pdf import convert_directory

    result = convert_directory(tmp_path, tmp_path)
    assert result == []


def test_convert_file_produces_pdf(tmp_path):
    from pdfcraft.converters.md_to_pdf import convert_file

    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\nHello world.", encoding="utf-8")

    pdf_path = convert_file(md_file, tmp_path)

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 0


def test_convert_directory_converts_all(tmp_path):
    from pdfcraft.converters.md_to_pdf import convert_directory

    (tmp_path / "a.md").write_text("# A", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B", encoding="utf-8")

    results = convert_directory(tmp_path, tmp_path)

    assert len(results) == 2
    for path in results:
        assert path.exists()
        assert path.suffix == ".pdf"
