"""Sanity checks on the bundled database itself."""

from __future__ import annotations

from mimedb import iter_types
from mimedb._database import DATABASE


def test_database_has_at_least_120_entries() -> None:
    assert len(DATABASE) >= 120


def test_every_entry_has_at_least_one_extension() -> None:
    for entry in DATABASE:
        mime, *extensions = entry
        assert mime
        assert extensions, f"{mime} has no extensions"


def test_every_extension_is_a_string() -> None:
    for entry in DATABASE:
        for extension in entry[1:]:
            assert isinstance(extension, str)
            assert extension == extension.strip()


def test_known_canonical_types_are_present() -> None:
    types = set(iter_types())
    for required in (
        "image/png",
        "image/jpeg",
        "application/json",
        "application/pdf",
        "text/html",
        "text/markdown",
        "audio/mpeg",
        "video/mp4",
        "font/woff2",
        "application/zip",
    ):
        assert required in types


def test_database_is_a_tuple_of_tuples() -> None:
    assert isinstance(DATABASE, tuple)
    for entry in DATABASE:
        assert isinstance(entry, tuple)
