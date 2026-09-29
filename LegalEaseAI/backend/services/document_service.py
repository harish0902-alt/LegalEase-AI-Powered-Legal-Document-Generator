import html
import re


def sanitize_text(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def extract_terms(raw_terms: str) -> list[str]:
    parts = re.split(r"[;\n]+", raw_terms)

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def format_html_preview(text: str) -> str:
    escaped = html.escape(text)

    return escaped.replace(
        "\n",
        "<br>",
    )