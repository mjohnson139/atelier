"""``draw_note``: a titled card with a few lines of text.

The smallest real tool, used by the curator for findings on the board and by the
test harness to prove the golden pipeline. Text is set in a monospace face so width
can be computed without font metrics, which keeps rendering deterministic.
"""

import hashlib
from typing import Literal

from pydantic import Field

from atelier_kit.spec import Spec
from atelier_kit.svg import escape, fmt

Tone = Literal["neutral", "finding", "risk"]

# Accent colours per tone, matching the concept page's pencils.
_ACCENT: dict[Tone, str] = {
    "neutral": "#4a5263",
    "finding": "#2f5bd3",
    "risk": "#a86f00",
}

_CHAR_EM = 0.6  # advance width of IBM Plex Mono and most monospace faces, in ems
_PAD = 16.0
_TITLE_SIZE = 16.0
_BODY_SIZE = 14.0
_LINE_HEIGHT = 20.0
_MIN_WIDTH = 160.0
_ACCENT_WIDTH = 4.0


class NoteSpec(Spec):
    """A card with a title and up to twelve short lines."""

    title: str = Field(min_length=1, max_length=60)
    lines: list[str] = Field(default_factory=list, max_length=12)
    tone: Tone = "neutral"


def render(spec: NoteSpec) -> str:
    """Render a note card to a standalone SVG string."""
    text_width = max(
        [len(spec.title) * _TITLE_SIZE * _CHAR_EM]
        + [len(line) * _BODY_SIZE * _CHAR_EM for line in spec.lines]
    )
    width = max(_MIN_WIDTH, _PAD * 2 + _ACCENT_WIDTH + text_width)
    height = _PAD * 2 + _TITLE_SIZE + len(spec.lines) * _LINE_HEIGHT + (8 if spec.lines else 0)
    accent = _ACCENT[spec.tone]
    text_x = _PAD + _ACCENT_WIDTH
    # Ids must be unique when several notes are inlined in one page (the board), and
    # stable across runs (the goldens), so derive them from the spec itself.
    clip_id = "note-" + hashlib.sha1(spec.model_dump_json().encode()).hexdigest()[:10]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" '
        f'viewBox="0 0 {fmt(width)} {fmt(height)}" font-family="IBM Plex Mono, monospace">',
        f'<clipPath id="{clip_id}"><rect x="0.5" y="0.5" width="{fmt(width - 1)}" '
        f'height="{fmt(height - 1)}" rx="8"/></clipPath>',
        f'<rect x="0.5" y="0.5" width="{fmt(width - 1)}" height="{fmt(height - 1)}" rx="8" '
        f'fill="#ffffff" stroke="#d9dfe8"/>',
        f'<rect x="0" y="0" width="{fmt(_ACCENT_WIDTH)}" height="{fmt(height)}" '
        f'fill="{accent}" clip-path="url(#{clip_id})"/>',
        f'<text x="{fmt(text_x)}" y="{fmt(_PAD + _TITLE_SIZE - 3)}" font-size="{fmt(_TITLE_SIZE)}" '
        f'font-weight="500" fill="#18202e">{escape(spec.title)}</text>',
    ]
    for index, line in enumerate(spec.lines):
        y = _PAD + _TITLE_SIZE + 8 + (index + 1) * _LINE_HEIGHT - 5
        parts.append(
            f'<text x="{fmt(text_x)}" y="{fmt(y)}" font-size="{fmt(_BODY_SIZE)}" '
            f'fill="#5a6475">{escape(line)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
