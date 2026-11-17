"""Atelier's drawing kit: declarative specs in, deterministic SVG out.

Every tool is a pure function from a validated spec to an SVG string. Nothing here
touches the network, the clock or a random source, so the same spec always renders
to the same bytes.
"""

from atelier_kit.registry import TOOLS, Tool, render_document
from atelier_kit.spec import Spec

__all__ = ["TOOLS", "Spec", "Tool", "render_document"]
__version__ = "0.0.0"
