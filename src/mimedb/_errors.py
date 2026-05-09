"""Error hierarchy for mimedb."""

from __future__ import annotations


class MimeDbError(ValueError):
    """Base class for every error raised by mimedb."""


class InvalidMimeTypeError(MimeDbError):
    """Raised when a string cannot be parsed as a media type."""


class UnknownMimeTypeError(MimeDbError):
    """Raised when a lookup misses a registered MIME type."""


class InvalidExtensionError(MimeDbError):
    """Raised when an extension argument is malformed."""
