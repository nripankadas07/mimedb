"""Category classification for parsed MIME types."""

from __future__ import annotations

from ._parse import parse
from ._types import ParsedMimeType

# Known top-level types per RFC 6838 plus a few `chemical/`-style
# unofficial categories that show up in practice.
_KNOWN_CATEGORIES: frozenset[str] = frozenset(
    {
        "application",
        "audio",
        "chemical",
        "example",
        "font",
        "image",
        "message",
        "model",
        "multipart",
        "text",
        "video",
    },
)

# `application/*` essences that should be treated as text for tooling
# purposes — JSON, XML, JS, etc.
_TEXTLIKE_APPLICATION_ESSENCES: frozenset[str] = frozenset(
    {
        "application/json",
        "application/javascript",
        "application/typescript",
        "application/ecmascript",
        "application/xml",
        "application/yaml",
        "application/toml",
        "application/sql",
        "application/x-www-form-urlencoded",
    },
)

_TEXTLIKE_SUFFIXES: frozenset[str] = frozenset({"json", "xml", "yaml"})


def category(mime_type: str | ParsedMimeType) -> str:
    """Return the top-level category, e.g. ``"image"``.

    The category is the lower-cased ``type/`` half. ``"unknown"`` is
    returned only when the type is not in :data:`_KNOWN_CATEGORIES`,
    which lets callers branch on a closed set.
    """
    parsed = _coerce(mime_type)
    if parsed.type_ in _KNOWN_CATEGORIES:
        return parsed.type_
    return "unknown"


def is_text(mime_type: str | ParsedMimeType) -> bool:
    """Whether the MIME type can be safely read as text.

    Anything under ``text/`` is text. ``application/*`` types whose
    essence is in :data:`_TEXTLIKE_APPLICATION_ESSENCES` or whose
    structured-syntax suffix is in :data:`_TEXTLIKE_SUFFIXES` (so
    ``application/vnd.api+json`` counts) are also text.
    """
    parsed = _coerce(mime_type)
    if parsed.type_ == "text":
        return True
    if parsed.type_ != "application":
        return False
    if parsed.essence in _TEXTLIKE_APPLICATION_ESSENCES:
        return True
    return parsed.suffix in _TEXTLIKE_SUFFIXES


def is_image(mime_type: str | ParsedMimeType) -> bool:
    """Convenience wrapper returning whether the type is ``image/*``."""
    return _coerce(mime_type).type_ == "image"


def is_audio(mime_type: str | ParsedMimeType) -> bool:
    """Convenience wrapper for ``audio/*``."""
    return _coerce(mime_type).type_ == "audio"


def is_video(mime_type: str | ParsedMimeType) -> bool:
    """Convenience wrapper for ``video/*``."""
    return _coerce(mime_type).type_ == "video"


def _coerce(mime_type: str | ParsedMimeType) -> ParsedMimeType:
    if isinstance(mime_type, ParsedMimeType):
        return mime_type
    return parse(mime_type)
