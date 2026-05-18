"""
pdfcraft — CLI entry point.

Commands:
    pdfcraft md-to-pdf <input_dir> [--output-dir <dir>]
    pdfcraft pdf-to-text <pdf_file> [--summarize] [--verbose]
"""

import argparse
import logging
import sys

from pdfcraft.utils.logging import configure_logging
from pdfcraft.utils.validation import require_directory, require_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdfcraft",
        description="PDF and Markdown conversion toolkit.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- md-to-pdf ---
    md_parser = sub.add_parser(
        "md-to-pdf",
        help="Convert all *.md files in a directory to PDF.",
    )
    md_parser.add_argument("input_dir", help="Directory containing .md files")
    md_parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for output PDFs (default: same as input_dir)",
    )

    # --- pdf-to-text ---
    pt_parser = sub.add_parser(
        "pdf-to-text",
        help="Convert a PDF to text, with optional AI summarization.",
    )
    pt_parser.add_argument("pdf_file", help="Path to the input PDF file")
    pt_parser.add_argument(
        "--summarize",
        action="store_true",
        help="Send extracted text to OpenAI and write an AI summary",
    )
    pt_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )

    return parser


def _cmd_md_to_pdf(args: argparse.Namespace) -> None:
    from pathlib import Path
    from pdfcraft.converters.md_to_pdf import convert_directory

    input_dir = require_directory(args.input_dir)
    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_dir

    pdfs = convert_directory(input_dir, output_dir)
    if not pdfs:
        sys.exit(1)


def _cmd_pdf_to_text(args: argparse.Namespace) -> None:
    from pdfcraft.converters.pdf_to_text import extract_pdf_to_text
    from pdfcraft.utils.files import derive_output_path, sanitize_filename, write_text_file
    from pdfcraft.utils.summarizer import summarize_with_openai

    configure_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    pdf_path = require_file(args.pdf_file)

    logger.info("Extracting text from: %s", pdf_path)
    text = extract_pdf_to_text(str(pdf_path))

    if not text.strip():
        logger.error("No readable content could be extracted from the PDF")
        sys.exit(1)

    output_path = derive_output_path(str(pdf_path))
    write_text_file(output_path, text)
    print(f"Text saved to: {output_path}")

    if args.summarize:
        logger.info("Requesting AI summary from OpenAI")
        try:
            suggested_name, summary = summarize_with_openai(text)
        except EnvironmentError as exc:
            logger.error("%s", exc)
            sys.exit(1)
        except ValueError as exc:
            logger.error("Summarization failed: %s", exc)
            sys.exit(1)

        summary_path = sanitize_filename(suggested_name, extension=".md")
        write_text_file(summary_path, summary)
        print(f"Summary saved to: {summary_path}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "md-to-pdf":
        configure_logging()
        _cmd_md_to_pdf(args)
    elif args.command == "pdf-to-text":
        _cmd_pdf_to_text(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
