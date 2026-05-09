"""mimedb — MIME-type ↔ extension lookup with category classification."""

from __future__ import annotations

from ._categories import (
    category,
    is_audio,
    is_image,
    is_text,
    is_video,
)
from ._errors import (
    InvalidExtensionError,
    InvalidMimeTypeError,
    MimeDbError,
    UnknownMimeTypeError,
)
from ._lookup import (
    extension_for,
    extensions_for,
    iter_types,
    lookup,
    mime_for_extension,
    mime_for_filename,
    register,
    unregister,
)
from ._parse import format_mime, parse
from ._types import ParsedMimeType

__all__ = [
    "InvalidExtensionError",
    "InvalidMimeTypeError",
    "MimeDbError",
    "ParsedMimeType",
    "UnknownMimeTypeError",
    "category",
    "extension_for",
    "extensions_for",
    "format_mime",
    "is_audio",
    "is_image",
    "is_text",
    "is_video",
    "iter_types",
    "lookup",
    "mime_for_extension",
    "mime_for_filename",
    "parse",
    "register",
    "unregister",
]

__version__ = "0.1.0"
