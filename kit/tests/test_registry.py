import pytest

from atelier_kit import TOOLS, render_document


def test_tools_are_registered_by_name() -> None:
    assert "draw_note" in TOOLS
    assert all(name == tool.name for name, tool in TOOLS.items())


def test_render_document() -> None:
    svg = render_document({"tool": "draw_note", "spec": {"title": "Hi"}})
    assert "Hi" in svg


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ({"tool": "draw_nothing", "spec": {}}, "unknown tool"),
        ({"spec": {}}, "unknown tool"),
        ({"tool": "draw_note", "spec": []}, "must be an object"),
    ],
)
def test_render_document_rejects_bad_documents(document: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        render_document(document)
