"""Public surface — every documented name exists with the right kind."""

from __future__ import annotations

import inspect

import mimedb


def test_top_level_module_has_all_attribute() -> None:
    assert isinstance(mimedb.__all__, list)
    assert "parse" in mimedb.__all__
    assert "extension_for" in mimedb.__all__


def test_callables_are_callable() -> None:
    for name in (
        "parse",
        "format_mime",
        "extension_for",
        "extensions_for",
        "mime_for_extension",
        "mime_for_filename",
        "category",
        "is_text",
        "is_image",
        "is_audio",
        "is_video",
        "iter_types",
        "lookup",
        "register",
        "unregister",
    ):
        assert callable(getattr(mimedb, name)), name


def test_error_hierarchy() -> None:
    assert issubclass(mimedb.MimeDbError, ValueError)
    assert issubclass(mimedb.InvalidMimeTypeError, mimedb.MimeDbError)
    assert issubclass(mimedb.UnknownMimeTypeError, mimedb.MimeDbError)
    assert issubclass(mimedb.InvalidExtensionError, mimedb.MimeDbError)


def test_parsed_mime_type_is_a_dataclass() -> None:
    parsed = mimedb.ParsedMimeType("text", "html")
    assert parsed.type_ == "text"
    assert parsed.subtype == "html"
    assert parsed.essence == "text/html"
    assert parsed.base == "text/html"


def test_iter_types_returns_iterator() -> None:
    assert inspect.isgenerator(iter(mimedb.iter_types()))
