"""Output pipeline: spec document -> SVG -> PNG -> files on disk, plus ``look``.

``write_view`` validates and renders a spec document, rasterises the SVG with resvg
and writes ``<name>.spec.json``, ``<name>.svg`` and ``<name>.png`` under
``<root>/views/<perspective>/``. resvg is a Rust library in a wheel, so there is no
system library to install, and the two IBM Plex Mono files shipped in the package
are the only fonts it may use, so the same SVG gives the same PNG bytes on any
machine. Nothing here touches the network.
"""

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import resvg_py

from atelier_kit.registry import render_document

PNG_MEDIA_TYPE = "image/png"
PNG_SCALE = 2.0  # device pixels per SVG unit, so text stays legible when a model looks

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_FONT_FAMILY = "IBM Plex Mono"
_FONTS_DIR = Path(__file__).parent / "fonts"
_NAME_RULE = "^[a-z0-9][a-z0-9-]{0,63}$"
_NAME_RE = re.compile(_NAME_RULE)
# Device names Windows will not treat as files, whatever the extension.
_RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{dev}{n}" for dev in ("com", "lpt") for n in range(10)
}


@dataclass(frozen=True)
class ViewPaths:
    """Where ``write_view`` put the three files of one view."""

    spec: Path
    svg: Path
    png: Path


@dataclass(frozen=True)
class Image:
    """A PNG's bytes with its media type, ready to hand back to a model."""

    data: bytes
    media_type: str


def svg_to_png(svg: str) -> bytes:
    """Rasterise an SVG string. Pure: the same SVG always gives the same bytes."""
    font_files = sorted(str(p) for p in _FONTS_DIR.glob("*.ttf"))
    # An opaque background so a viewer never shows a transparent card on black. Every
    # generic family is pinned to the vendored font so none resolves to nothing.
    return bytes(
        resvg_py.svg_to_bytes(
            svg_string=svg,
            font_files=font_files,
            skip_system_fonts=True,
            zoom=PNG_SCALE,
            background="#ffffff",
            font_family=_FONT_FAMILY,
            monospace_family=_FONT_FAMILY,
            sans_serif_family=_FONT_FAMILY,
            serif_family=_FONT_FAMILY,
        )
    )


def _check_name(argument: str, value: str) -> None:
    if not _NAME_RE.fullmatch(value):
        raise ValueError(
            f"invalid {argument} {value!r}: use 1 to 64 lowercase letters, digits or "
            f"hyphens, starting with a letter or digit (pattern {_NAME_RULE})"
        )
    if value in _RESERVED:
        raise ValueError(f"invalid {argument} {value!r}: Windows reserves that name; pick another")


def _is_inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _replace(path: Path, data: bytes) -> None:
    """Write beside ``path`` and rename over it, so a reader never sees half a file."""
    scratch = path.with_name(f".{path.name}.tmp")
    try:
        scratch.write_bytes(data)
        os.replace(scratch, path)
    finally:
        scratch.unlink(missing_ok=True)


def write_view(document: Mapping[str, Any], perspective: str, name: str, root: Path) -> ViewPaths:
    """Render ``document`` and write its spec, SVG and PNG under ``root``.

    Writing the same perspective and name again overwrites the view. Nothing is
    created on disk if validation or rendering fails.
    """
    _check_name("perspective", perspective)
    _check_name("name", name)
    if not root.is_dir():
        raise ValueError(f"root {str(root)!r} is not an existing directory")

    svg = render_document(document)
    png = svg_to_png(svg)

    resolved_root = root.resolve()
    target = resolved_root / "views" / perspective
    # resolve() follows symlinks, so a `views` or perspective link pointing out of
    # root is caught here, before anything is created or written.
    if not _is_inside(target.resolve(), resolved_root):
        raise ValueError(f"view directory {str(target)!r} resolves outside {str(resolved_root)!r}")
    target.mkdir(parents=True, exist_ok=True)

    paths = ViewPaths(
        spec=target / f"{name}.spec.json",
        svg=target / f"{name}.svg",
        png=target / f"{name}.png",
    )
    for path in (paths.spec, paths.svg, paths.png):
        if path.is_symlink():
            raise ValueError(f"refusing to write through symlink {str(path)!r}")

    spec_text = (
        json.dumps(
            {"tool": document["tool"], "spec": document["spec"]}, indent=2, ensure_ascii=False
        )
        + "\n"
    )
    # The PNG goes last: it is what `look` reads, so it never runs ahead of its spec.
    _replace(paths.spec, spec_text.encode("utf-8"))
    _replace(paths.svg, svg.encode("utf-8"))
    _replace(paths.png, png)
    return paths


def look(path: Path, root: Path | None = None) -> Image:
    """Return a PNG file's bytes and media type.

    Only PNGs are readable, and only inside ``root`` when one is given, so this
    cannot be used to read arbitrary files.
    """
    if root is not None and not _is_inside(path.resolve(), root.resolve()):
        raise ValueError(f"{str(path)!r} is outside {str(root)!r}; look only reads inside it")
    if not path.exists():
        raise ValueError(f"{str(path)!r} does not exist")
    if not path.is_file():
        raise ValueError(f"{str(path)!r} is not a file")
    with path.open("rb") as file:
        # Check the signature before reading on, so a large non-PNG is never loaded.
        head = file.read(len(_PNG_SIGNATURE))
        if head != _PNG_SIGNATURE:
            raise ValueError(f"{str(path)!r} is not a PNG file")
        data = head + file.read()
    return Image(data=data, media_type=PNG_MEDIA_TYPE)
