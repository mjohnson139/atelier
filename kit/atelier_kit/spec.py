"""The base every kit spec builds on."""

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

# Characters XML 1.0 cannot carry: C0 controls other than tab, newline and carriage
# return, lone surrogates, and U+FFFE/U+FFFF.
_NOT_XML = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]")


def _find_bad_text(value: Any, path: str) -> str | None:
    if isinstance(value, str):
        return path if _NOT_XML.search(value) else None
    if isinstance(value, BaseModel):
        value = dict(value)
    if isinstance(value, dict):
        items: list[tuple[str, Any]] = [(f"{path}.{key}", item) for key, item in value.items()]
    elif isinstance(value, list | tuple):
        items = [(f"{path}[{index}]", item) for index, item in enumerate(value)]
    else:
        return None
    for item_path, item in items:
        found = _find_bad_text(item, item_path)
        if found:
            return found
    return None


class Spec(BaseModel):
    """A drawing request from a perspective.

    Specs are frozen and reject unknown fields, so a typo in a model-written spec is
    a validation error the model can read and fix, not a silently ignored key. Text
    that SVG cannot hold (control characters) is rejected the same way.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    @model_validator(mode="after")
    def _text_is_xml_safe(self) -> "Spec":
        found = _find_bad_text(dict(self), "spec")
        if found:
            raise ValueError(f"{found} contains a control character SVG cannot hold")
        return self
