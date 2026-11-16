"""Golden tests: every spec in specs/ must render to its committed SVG.

A spec document is ``specs/<name>.json`` holding ``{"tool": ..., "spec": {...}}``;
its golden is ``specs/<name>.svg``. After an intended visual change, run
``make goldens``, look at the new SVGs, and commit them with the change.
"""

import json
from pathlib import Path

import pytest

from atelier_kit import render_document
from atelier_kit.svg import normalise_svg

SPECS = Path(__file__).parent / "specs"
SPEC_FILES = sorted(SPECS.glob("*.json"))


def test_there_are_golden_specs() -> None:
    assert SPEC_FILES, f"no golden specs found in {SPECS}"


@pytest.mark.parametrize("spec_file", SPEC_FILES, ids=lambda path: path.stem)
def test_golden(spec_file: Path, update_goldens: bool) -> None:
    rendered = render_document(json.loads(spec_file.read_text(encoding="utf-8")))
    golden = spec_file.with_suffix(".svg")

    if update_goldens:
        golden.write_text(rendered, encoding="utf-8")
        return

    assert golden.exists(), f"{golden.name} is missing; run `make goldens` and review it"
    assert normalise_svg(rendered) == normalise_svg(golden.read_text(encoding="utf-8")), (
        f"{spec_file.stem} no longer matches {golden.name}. If the change is intended, "
        "run `make goldens`, look at the new SVG, and commit it."
    )


def test_rendering_is_deterministic() -> None:
    for spec_file in SPEC_FILES:
        document = json.loads(spec_file.read_text(encoding="utf-8"))
        assert render_document(document) == render_document(document), spec_file.stem
