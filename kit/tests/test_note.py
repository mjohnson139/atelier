import re

import pytest
from pydantic import ValidationError

from atelier_kit.tools.note import NoteSpec, render


def _size(svg: str) -> tuple[float, float]:
    match = re.search(r'width="([\d.]+)" height="([\d.]+)"', svg)
    assert match
    return float(match.group(1)), float(match.group(2))


def test_minimal_note_renders_svg() -> None:
    svg = render(NoteSpec(title="Hello"))
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "Hello" in svg
    assert svg.endswith("</svg>\n")


def test_text_is_escaped() -> None:
    svg = render(NoteSpec(title="a < b", lines=['x & "y"']))
    assert "a &lt; b" in svg
    assert "x &amp; &quot;y&quot;" in svg


def test_height_grows_with_lines_and_width_with_text() -> None:
    short = _size(render(NoteSpec(title="T")))
    tall = _size(render(NoteSpec(title="T", lines=["one", "two"])))
    wide = _size(render(NoteSpec(title="T" * 50)))
    assert tall[1] > short[1]
    assert wide[0] > short[0]


@pytest.mark.parametrize(
    "data",
    [
        {"title": ""},
        {"title": "   "},
        {"title": "ok", "colour": "red"},
        {"title": "ok", "tone": "loud"},
        {"title": "ok", "lines": ["x"] * 13},
    ],
)
def test_invalid_specs_are_rejected(data: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        NoteSpec.model_validate(data)


def test_ids_are_unique_per_note_and_stable() -> None:
    a = render(NoteSpec(title="One"))
    b = render(NoteSpec(title="Two"))
    ids = [re.search(r'clipPath id="([^"]+)"', svg) for svg in (a, b)]
    assert ids[0] and ids[1]
    assert ids[0].group(1) != ids[1].group(1)
    assert render(NoteSpec(title="One")) == a


def test_title_width_accounts_for_its_larger_size() -> None:
    title = "Untested transition"
    width, _ = _size(render(NoteSpec(title=title)))
    assert width >= 16 + 4 + len(title) * 16 * 0.6 + 16
