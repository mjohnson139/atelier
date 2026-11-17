"""Atelier's drawing kit: declarative specs in, deterministic SVG and PNG out.

Every tool is a pure function from a validated spec to an SVG string. Nothing here
touches the network, the clock or a random source, so the same spec always renders
to the same bytes.
"""

from atelier_kit.output import (
    PNG_MEDIA_TYPE,
    PNG_SCALE,
    Image,
    ViewPaths,
    look,
    svg_to_png,
    write_view,
)
from atelier_kit.registry import TOOLS, Tool, render_document
from atelier_kit.spec import Spec

__all__ = [
    "PNG_MEDIA_TYPE",
    "PNG_SCALE",
    "TOOLS",
    "Image",
    "Spec",
    "Tool",
    "ViewPaths",
    "look",
    "render_document",
    "svg_to_png",
    "write_view",
]
__version__ = "0.0.0"
