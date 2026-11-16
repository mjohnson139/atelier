"""The base every kit spec builds on."""

from pydantic import BaseModel, ConfigDict


class Spec(BaseModel):
    """A drawing request from a perspective.

    Specs are frozen and reject unknown fields, so a typo in a model-written spec is
    a validation error the model can read and fix, not a silently ignored key.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)
