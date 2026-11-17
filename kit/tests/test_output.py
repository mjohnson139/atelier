"""Tests for the output pipeline: PNG rendering, files on disk and ``look``."""

import json
import math
import re
import socket
import struct
import sys
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from atelier_kit import PNG_MEDIA_TYPE, Image, look, render_document, svg_to_png, write_view
from atelier_kit.output import _FONTS_DIR

SPECS = Path(__file__).parent / "specs"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

needs_symlinks = pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges")


@pytest.fixture
def document() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads((SPECS / "note-basic.json").read_text(encoding="utf-8"))
    return loaded


def _png_size(data: bytes) -> tuple[int, int]:
    width, height = struct.unpack(">II", data[16:24])
    return int(width), int(height)


def test_write_view_writes_three_files(tmp_path: Path, document: dict[str, Any]) -> None:
    paths = write_view(document, "designer", "board", tmp_path)
    directory = tmp_path.resolve() / "views" / "designer"
    assert paths.spec == directory / "board.spec.json"
    assert paths.svg == directory / "board.svg"
    assert paths.png == directory / "board.png"
    assert sorted(p.name for p in directory.iterdir()) == [
        "board.png",
        "board.spec.json",
        "board.svg",
    ]
    assert json.loads(paths.spec.read_text(encoding="utf-8")) == {
        "tool": document["tool"],
        "spec": document["spec"],
    }
    assert paths.svg.read_text(encoding="utf-8") == render_document(document)
    assert paths.png.read_bytes().startswith(PNG_SIGNATURE)


def test_spec_file_round_trips(tmp_path: Path, document: dict[str, Any]) -> None:
    paths = write_view(document, "designer", "board", tmp_path)
    again = render_document(json.loads(paths.spec.read_text(encoding="utf-8")))
    assert again == paths.svg.read_text(encoding="utf-8")


def test_png_size_follows_svg_size(document: dict[str, Any]) -> None:
    svg = render_document(document)
    match = re.search(r'width="([\d.]+)" height="([\d.]+)"', svg)
    assert match is not None
    expected = (math.ceil(float(match[1]) * 2), math.ceil(float(match[2]) * 2))
    assert _png_size(svg_to_png(svg)) == expected == (728, 192)


def test_output_is_deterministic(tmp_path: Path, document: dict[str, Any]) -> None:
    svg = render_document(document)
    assert svg_to_png(svg) == svg_to_png(svg)
    (a, b) = (tmp_path / "a", tmp_path / "b")
    a.mkdir()
    b.mkdir()
    first = write_view(document, "designer", "board", a)
    second = write_view(document, "designer", "board", b)
    for one, two in ((first.png, second.png), (first.svg, second.svg), (first.spec, second.spec)):
        assert one.read_bytes() == two.read_bytes()


def test_text_is_drawn_with_vendored_font(document: dict[str, Any]) -> None:
    svg = render_document(document)
    without_text = re.sub(r"<text\b.*?</text>", "", svg, flags=re.DOTALL)
    assert without_text != svg
    assert svg_to_png(svg) != svg_to_png(without_text)


def test_second_write_overwrites(tmp_path: Path, document: dict[str, Any]) -> None:
    first = write_view(document, "designer", "board", tmp_path)
    before = first.png.read_bytes()
    revised = {"tool": "draw_note", "spec": {"title": "Revised", "lines": ["new"]}}
    second = write_view(revised, "designer", "board", tmp_path)
    assert second == first
    assert second.png.read_bytes() != before
    assert json.loads(second.spec.read_text(encoding="utf-8"))["spec"]["title"] == "Revised"
    assert "Revised" in second.svg.read_text(encoding="utf-8")
    assert len(list(second.png.parent.iterdir())) == 3


def test_extra_document_keys_are_not_written(tmp_path: Path, document: dict[str, Any]) -> None:
    paths = write_view({**document, "note": "private"}, "designer", "board", tmp_path)
    written = json.loads(paths.spec.read_text(encoding="utf-8"))
    assert list(written) == ["tool", "spec"]


@pytest.mark.parametrize("argument", ["perspective", "name"])
@pytest.mark.parametrize(
    "bad",
    ["", "..", ".", "a/b", "../x", "/abs", "a\\b", "Upper", "has space", "a.b", "x" * 65],
)
def test_bad_names_rejected(
    tmp_path: Path, document: dict[str, Any], argument: str, bad: str
) -> None:
    names = {"perspective": "designer", "name": "board"}
    names[argument] = bad
    with pytest.raises(ValueError, match=argument):
        write_view(document, names["perspective"], names["name"], tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("bad", "error"),
    [
        ({"tool": "nope", "spec": {}}, ValueError),
        ({"tool": "draw_note", "spec": {"title": "t", "lines": [], "bogus": 1}}, ValidationError),
    ],
)
def test_invalid_document_leaves_root_empty(
    tmp_path: Path, bad: dict[str, Any], error: type[Exception]
) -> None:
    with pytest.raises(error):
        write_view(bad, "designer", "board", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_missing_root_rejected(tmp_path: Path, document: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="root"):
        write_view(document, "designer", "board", tmp_path / "missing")


@needs_symlinks
def test_views_symlink_out_of_root_rejected(tmp_path: Path, document: dict[str, Any]) -> None:
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "views").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="outside"):
        write_view(document, "designer", "board", root)
    assert list(outside.iterdir()) == []


@needs_symlinks
def test_perspective_symlink_out_of_root_rejected(tmp_path: Path, document: dict[str, Any]) -> None:
    root, outside = tmp_path / "root", tmp_path / "outside"
    (root / "views").mkdir(parents=True)
    outside.mkdir()
    (root / "views" / "designer").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="outside"):
        write_view(document, "designer", "board", root)
    assert list(outside.iterdir()) == []


@needs_symlinks
def test_target_file_symlink_rejected(tmp_path: Path, document: dict[str, Any]) -> None:
    root, outside = tmp_path / "root", tmp_path / "outside"
    (root / "views" / "designer").mkdir(parents=True)
    outside.mkdir()
    victim = outside / "victim.png"
    victim.write_bytes(b"keep")
    (root / "views" / "designer" / "board.png").symlink_to(victim)
    with pytest.raises(ValueError, match="symlink"):
        write_view(document, "designer", "board", root)
    assert victim.read_bytes() == b"keep"


def test_no_network_used(
    tmp_path: Path, document: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("network used while rendering")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    paths = write_view(document, "designer", "board", tmp_path)
    assert look(paths.png, tmp_path).data.startswith(PNG_SIGNATURE)


def test_look_returns_png(tmp_path: Path, document: dict[str, Any]) -> None:
    paths = write_view(document, "designer", "board", tmp_path)
    assert look(paths.png) == Image(paths.png.read_bytes(), PNG_MEDIA_TYPE)
    assert look(paths.png).media_type == "image/png"


def test_look_rejects_non_png_inputs(tmp_path: Path, document: dict[str, Any]) -> None:
    paths = write_view(document, "designer", "board", tmp_path)
    with pytest.raises(ValueError, match="does not exist"):
        look(tmp_path / "missing.png")
    with pytest.raises(ValueError, match="not a file"):
        look(tmp_path)
    with pytest.raises(ValueError, match="not a PNG"):
        look(paths.svg)


def test_look_respects_root(tmp_path: Path, document: dict[str, Any]) -> None:
    root, other = tmp_path / "root", tmp_path / "other"
    root.mkdir()
    other.mkdir()
    inside = write_view(document, "designer", "board", root)
    outside = write_view(document, "designer", "board", other)
    assert look(inside.png, root).media_type == PNG_MEDIA_TYPE
    with pytest.raises(ValueError, match="outside"):
        look(outside.png, root)


def test_vendored_fonts_exist() -> None:
    for font in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
        assert (_FONTS_DIR / font).stat().st_size > 0
