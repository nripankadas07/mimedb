"""Lookup helpers — MIME ↔ extension and filename inference."""

from __future__ import annotations

import os
from typing import Iterator

from ._database import DATABASE
from ._errors import InvalidExtensionError, UnknownMimeTypeError
from ._parse import parse


def _build_indexes() -> tuple[
    dict[str, tuple[str, ...]], dict[str, str],
]:
    extensions_by_mime: dict[str, tuple[str, ...]] = {}
    mime_by_extension: dict[str, str] = {}
    for entry in DATABASE:
        mime, *extensions = entry
        canonical = mime.lower()
        existing = extensions_by_mime.get(canonical, ())
        extensions_by_mime[canonical] = existing + tuple(extensions)
        for extension in extensions:
            normalised = extension.lower()
            mime_by_extension.setdefault(normalised, mime)
    return extensions_by_mime, mime_by_extension


_EXTENSIONS_BY_MIME, _MIME_BY_EXTENSION = _build_indexes()
_USER_EXTENSIONS_BY_MIME: dict[str, tuple[str, ...]] = {}
_USER_MIME_BY_EXTENSION: dict[str, str] = {}


def extension_for(mime_type: str) -> str | None:
    """Primary extension for ``mime_type`` (no leading dot)."""
    extensions = extensions_for(mime_type)
    if not extensions:
        return None
    return extensions[0]


def extensions_for(mime_type: str) -> list[str]:
    """All known extensions for ``mime_type``, in registered order."""
    canonical = parse(mime_type).base
    user = _USER_EXTENSIONS_BY_MIME.get(canonical, ())
    builtin = _EXTENSIONS_BY_MIME.get(canonical, ())
    seen: set[str] = set()
    ordered: list[str] = []
    for extension in (*user, *builtin):
        normalised = extension.lower()
        if normalised in seen:
            continue
        seen.add(normalised)
        ordered.append(normalised)
    return ordered


def mime_for_extension(extension: str) -> str | None:
    """Return the canonical MIME type for an extension, or ``None``."""
    if not isinstance(extension, str):
        raise InvalidExtensionError(
            f"extension must be str, got {type(extension).__name__}",
        )
    normalised = extension.lstrip(".").lower()
    if not normalised:
        raise InvalidExtensionError("extension is empty")
    if normalised in _USER_MIME_BY_EXTENSION:
        return _USER_MIME_BY_EXTENSION[normalised]
    return _MIME_BY_EXTENSION.get(normalised)


def mime_for_filename(filename: str) -> str | None:
    """Infer the MIME type from a filename's last extension component."""
    if not isinstance(filename, str):
        raise InvalidExtensionError(
            f"filename must be str, got {type(filename).__name__}",
        )
    base = os.path.basename(filename)
    if not base:
        return None
    _, dot, extension = base.rpartition(".")
    if not dot:
        return None
    return mime_for_extension(extension)


def iter_types() -> Iterator[str]:
    """Yield every registered MIME type (built-ins followed by user)."""
    seen: set[str] = set()
    for mime in (*_EXTENSIONS_BY_MIME, *_USER_EXTENSIONS_BY_MIME):
        if mime in seen:
            continue
        seen.add(mime)
        yield mime


def lookup(mime_type: str) -> tuple[str, ...]:
    """Return the extension tuple for ``mime_type`` or raise.

    Stricter sibling of :func:`extensions_for` — useful when the caller
    wants an error rather than an empty list for unknown types.
    """
    extensions = extensions_for(mime_type)
    if not extensions:
        raise UnknownMimeTypeError(f"unknown MIME type: {mime_type!r}")
    return tuple(extensions)


def register(mime_type: str, extensions: list[str] | tuple[str, ...]) -> None:
    """Register a custom MIME ↔ extension mapping at runtime."""
    canonical = parse(mime_type).base
    if not extensions:
        raise InvalidExtensionError("extensions list is empty")
    normalised: list[str] = []
    for extension in extensions:
        if not isinstance(extension, str) or not extension.strip("."):
            raise InvalidExtensionError(
                f"invalid extension {extension!r}",
            )
        normalised.append(extension.lstrip(".").lower())
    existing = _USER_EXTENSIONS_BY_MIME.get(canonical, ())
    _USER_EXTENSIONS_BY_MIME[canonical] = existing + tuple(normalised)
    for extension in normalised:
        _USER_MIME_BY_EXTENSION.setdefault(extension, canonical)


def unregister(mime_type: str) -> bool:
    """Remove a previously :func:`register`ed MIME type. Returns ``True``
    when an entry was removed, ``False`` if the type was not registered.
    """
    canonical = parse(mime_type).base
    extensions = _USER_EXTENSIONS_BY_MIME.pop(canonical, None)
    if extensions is None:
        return False
    for extension in extensions:
        if _USER_MIME_BY_EXTENSION.get(extension) == canonical:
            _USER_MIME_BY_EXTENSION.pop(extension, None)
    return True
