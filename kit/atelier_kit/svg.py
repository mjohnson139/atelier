"""Small SVG helpers shared by the tools and the golden tests."""

import re
from xml.sax.saxutils import escape as _escape

_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_XML_DECL = re.compile(r"<\?xml[^>]*\?>")
_BETWEEN_TAGS = re.compile(r">\s+<")
_FLOAT = re.compile(r"-?\d+\.\d+")


def escape(text: str) -> str:
    """Escape text for use in SVG element content or a double-quoted attribute."""
    return _escape(text, {'"': "&quot;"})


def fmt(value: float) -> str:
    """Format a coordinate with at most two decimals and no trailing zeros."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def _round_float(match: re.Match[str]) -> str:
    return fmt(float(match.group(0)))


def normalise_svg(svg: str) -> str:
    """Reduce an SVG to the parts that matter for a golden comparison.

    Drops comments and the XML declaration, collapses whitespace between tags and
    rounds every decimal number to two places, so renderer noise (a float printed
    as 10.000001, a reflowed line) does not fail a test while a moved shape does.
    """
    out = _COMMENT.sub("", svg)
    out = _XML_DECL.sub("", out)
    out = _BETWEEN_TAGS.sub("><", out.strip())
    return _FLOAT.sub(_round_float, out)
