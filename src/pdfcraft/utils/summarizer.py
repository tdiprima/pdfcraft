"""
Summarize text via OpenAI and get a suggested output filename.

Reads OPENAI_API_KEY from the environment. Sends the full extracted
text to GPT and asks for a JSON response containing the summary and
a suggested filename.
"""

import json
import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)

MODEL = "gpt-5.5"

_PROMPT_TEMPLATE = """\
This article is too long for me to read through completely. Can you give me \
the essential points in a way that's easy to scan and remember? Use complete \
sentences. Paraphrase to make things easier to understand.

Format the summary as proper Markdown. Use a top-level heading for the title, \
then second-level headings to organize the key sections. Keep the total length \
considerably shorter than the original — aim for the most important points only, \
not a restatement of everything.

Also suggest a concise filename for saving this summary \
(no extension, no spaces — use hyphens or underscores).

Respond with a JSON object containing exactly two fields:
  "filename": the suggested filename string (no extension)
  "summary": the full summary in Markdown format

Article:
{text}
"""


def summarize_with_openai(text: str) -> tuple[str, str]:
    """
    Send text to OpenAI and return (suggested_filename, summary).

    Raises EnvironmentError if OPENAI_API_KEY is not set.
    Raises ValueError if the model response cannot be parsed.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=api_key)
    prompt = _PROMPT_TEMPLATE.format(text=text)

    logger.info("Sending %d characters to %s for summarization", len(text), MODEL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model returned non-JSON response: {raw!r}") from exc

    filename = data.get("filename") or "summary"
    summary = data.get("summary") or ""

    return filename, summary
