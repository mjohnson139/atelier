"""Every kit tool, by the name a perspective calls it with."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from atelier_kit.spec import Spec
from atelier_kit.tools import note


@dataclass(frozen=True)
class Tool[S: Spec]:
    """A kit tool: its spec type and the pure function that renders it.

    Generic in the spec type, so mypy rejects a renderer paired with the wrong spec.
    """

    name: str
    spec_type: type[S]
    render: Callable[[S], str]

    def render_data(self, data: Mapping[str, Any]) -> str:
        """Validate raw spec data and render it to SVG."""
        return self.render(self.spec_type.model_validate(data))


TOOLS: dict[str, Tool[Any]] = {
    tool.name: tool for tool in (Tool("draw_note", note.NoteSpec, note.render),)
}


def render_document(document: Mapping[str, Any]) -> str:
    """Render a spec document of the form ``{"tool": "<name>", "spec": {...}}``."""
    name = document.get("tool")
    if not isinstance(name, str) or name not in TOOLS:
        known = ", ".join(sorted(TOOLS))
        raise ValueError(f"unknown tool {name!r}; known tools: {known}")
    spec = document.get("spec")
    if not isinstance(spec, Mapping):
        raise ValueError(f"{name}: 'spec' must be an object")
    return TOOLS[name].render_data(spec)
