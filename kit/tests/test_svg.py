import pytest

from atelier_kit.svg import escape, fmt, normalise_svg


@pytest.mark.parametrize(
    ("value", "expected"),
    [(10.0, "10"), (10.5, "10.5"), (10.456, "10.46"), (-0.001, "0"), (0.0, "0"), (-2.25, "-2.25")],
)
def test_fmt(value: float, expected: str) -> None:
    assert fmt(value) == expected


def test_escape_handles_markup_and_quotes() -> None:
    assert escape('a < b & "c" > d') == "a &lt; b &amp; &quot;c&quot; &gt; d"


def test_normalise_ignores_comments_declaration_and_layout_whitespace() -> None:
    a = '<?xml version="1.0"?>\n<!-- made by x -->\n<svg>\n  <rect x="1.000001"/>\n</svg>\n'
    b = '<svg><rect x="1"/></svg>'
    assert normalise_svg(a) == normalise_svg(b)


def test_normalise_keeps_real_differences() -> None:
    assert normalise_svg('<svg><rect x="1"/></svg>') != normalise_svg('<svg><rect x="1.5"/></svg>')
    assert normalise_svg("<svg><text>a b</text></svg>") != normalise_svg(
        "<svg><text>a  b</text></svg>"
    )


def test_normalise_compares_text_content_exactly() -> None:
    assert normalise_svg("<svg><text>v1.234</text></svg>") != normalise_svg(
        "<svg><text>v1.231</text></svg>"
    )
    assert normalise_svg("<svg><text> </text></svg>") != normalise_svg("<svg><text></text></svg>")


def test_normalise_rounds_only_attribute_values() -> None:
    assert normalise_svg('<svg><rect x="1.0049"/></svg>') == '<svg><rect x="1"/></svg>'
    assert normalise_svg("<svg><text>1.0049</text></svg>") == "<svg><text>1.0049</text></svg>"
