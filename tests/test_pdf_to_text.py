"""Tests for the pdf-to-text converter and utilities."""

import pytest


def test_format_table_basic():
    from pdfcraft.converters.pdf_to_text import _format_table

    table = [["Name", "Value"], ["Alpha", "1"], ["Beta", "2"]]
    result = _format_table(table)
    assert "Name | Value" in result
    assert "Alpha | 1" in result


def test_format_table_none_cells():
    from pdfcraft.converters.pdf_to_text import _format_table

    table = [[None, "B"], ["C", None]]
    result = _format_table(table)
    assert " | B" in result
    assert "C | " in result


def test_derive_output_path():
    from pdfcraft.utils.files import derive_output_path

    assert derive_output_path("/tmp/report.pdf") == "/tmp/report.txt"
    assert derive_output_path("file.pdf") == "file.txt"


def test_sanitize_filename_safe():
    from pdfcraft.utils.files import sanitize_filename

    assert sanitize_filename("my-report", ".md") == "my-report.md"


def test_sanitize_filename_strips_unsafe():
    from pdfcraft.utils.files import sanitize_filename

    result = sanitize_filename("hello world!@#", ".txt")
    assert " " not in result
    assert "!" not in result
    assert result.endswith(".txt")


def test_sanitize_filename_empty_falls_back():
    from pdfcraft.utils.files import sanitize_filename

    assert sanitize_filename("!!!") == "summary.txt"


def test_write_text_file(tmp_path):
    from pdfcraft.utils.files import write_text_file

    path = str(tmp_path / "out.txt")
    write_text_file(path, "hello")
    with open(path, encoding="utf-8") as fh:
        assert fh.read() == "hello"


def test_summarizer_raises_without_api_key(monkeypatch):
    from pdfcraft.utils.summarizer import summarize_with_openai

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        summarize_with_openai("some text")
