"""Public dataclasses used by mimedb."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ParsedMimeType:
    """A parsed media type, e.g. ``text/html; charset=utf-8``.

    ``type_`` and ``subtype`` are the two halves of the slash form,
    each lower-cased. ``suffix`` is the structured-syntax suffix without
    the leading ``+`` (e.g. ``"json"`` for ``application/vnd.api+json``)
    or ``None`` when absent. ``parameters`` is an ordered mapping with
    lower-cased keys; values keep their original casing because some
    consumers compare them verbatim (e.g. boundary tokens).
    """

    type_: str
    subtype: str
    suffix: str | None = None
    parameters: Mapping[str, str] = field(default_factory=dict)

    @property
    def essence(self) -> str:
        """``type/subtype`` with suffix and parameters stripped."""
        return f"{self.type_}/{self.subtype}"

    @property
    def base(self) -> str:
        """``type/subtype[+suffix]`` without parameters."""
        if self.suffix is None:
            return self.essence
        return f"{self.essence}+{self.suffix}"
