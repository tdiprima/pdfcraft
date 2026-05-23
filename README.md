# pdfcraft

A Python CLI for converting between Markdown and PDF, and extracting structured text from PDFs — including tables and embedded images, with optional AI summarization.

## PDFs and Markdown don't play nicely with standard tools

Markdown-to-PDF converters often produce plain, unstyled output that ignores tables, code blocks, and emoji. Going the other direction is messier: basic PDF extractors drop tables, ignore images entirely, and silently discard content, leaving you with a `.txt` file that looks fine until you notice half the data is missing. Research papers, reports, and technical documents are especially bad — they're full of multi-column layouts, figures with captions, and data tables that most tools mangle or skip.

## Three passes, nothing left behind

`pdfcraft` handles both directions cleanly.

When converting **Markdown to PDF**, it renders through an HTML intermediate using WeasyPrint, applying a typographically sensible stylesheet with emoji-compatible fonts, syntax-highlighted code blocks, tables, and a generated table of contents. The output is a properly formatted document, not a wall of unstyled text.

When converting **PDF to text**, it runs three passes per page: plain text via `pdfplumber`, table detection rendered as pipe-delimited rows, and OCR on embedded images via PyMuPDF and Tesseract. Everything is assembled in page order so context is preserved. Pass `--summarize` and the extracted text goes to GPT-5.5, which returns the key points as a Markdown document and picks a descriptive filename automatically.

## Example

A research paper with body text, a data table on page 4, and a chart image on page 9:

```
$ pdfcraft pdf-to-text quarterly-report.pdf --summarize

Text saved to: quarterly-report.txt
Summary saved to: q3-revenue-highlights-summary.md
```

`quarterly-report.txt` contains the full extraction, page-by-page, with tables and OCR'd image text inline. `q3-revenue-highlights-summary.md` is the GPT-5.5 summary, with a filename it chose based on the content.

A folder of Markdown notes:

```
$ pdfcraft md-to-pdf ./docs --output-dir ./pdfs

INFO converted docs/architecture.md -> pdfs/architecture.pdf
INFO converted docs/runbook.md -> pdfs/runbook.pdf
INFO Done. Converted 2 file(s), 0 error(s).
```

## Usage

### Install

```bash
uv sync
```

System dependencies are also required:

```bash
# macOS
brew install tesseract pango

# Ubuntu/Debian
sudo apt install tesseract-ocr libpango-1.0-0
```

For emoji rendering on Linux:

```bash
sudo apt install fonts-noto-color-emoji
```

Pip install

```sh
pip install -e .
```

### Markdown to PDF

```bash
# PDFs written alongside the .md files
pdfcraft md-to-pdf /path/to/docs

# PDFs written to a separate output folder
pdfcraft md-to-pdf /path/to/docs --output-dir /path/to/pdfs
```

### PDF to text

```bash
# Extract text, tables, and image OCR
pdfcraft pdf-to-text path/to/file.pdf

# Extract and summarize with GPT-5.5
OPENAI_API_KEY=sk-... pdfcraft pdf-to-text path/to/file.pdf --summarize

# Enable debug logging
pdfcraft pdf-to-text path/to/file.pdf --verbose
```

### Flags

| Command | Flag | Description |
|---|---|---|
| `pdf-to-text` | `--summarize` | Send extracted text to GPT-5.5 and write a Markdown summary |
| `pdf-to-text` | `--verbose`, `-v` | Enable debug logging |
| `md-to-pdf` | `--output-dir` | Directory for output PDFs (default: same as input) |

**Log level** can also be set via the `LOG_LEVEL` environment variable (`DEBUG`, `INFO`, `WARNING`).

<!--
Tests:

uv sync
uv run pytest

Verbose output:

uv run pytest -v

Run one file:

uv run pytest tests/test_md_to_pdf.py -v

Note: test_convert_file_produces_pdf and test_convert_directory_converts_all require WeasyPrint + Pango installed. All utils/pure-logic tests run without system deps.
-->

<br>
