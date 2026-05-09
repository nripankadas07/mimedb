"""Integration scenarios — exercise multiple modules end-to-end."""

from __future__ import annotations

from mimedb import (
    category,
    extension_for,
    format_mime,
    is_text,
    mime_for_filename,
    parse,
)


def test_parse_then_format_round_trip() -> None:
    samples = [
        "text/plain",
        "application/json",
        "image/svg+xml",
        "application/vnd.api+json",
        "text/html; charset=utf-8",
    ]
    for mime in samples:
        assert format_mime(parse(mime)) == mime


def test_filename_then_category_pipeline() -> None:
    mime = mime_for_filename("/Users/alice/photo.jpg")
    assert mime is not None
    assert category(mime) == "image"


def test_round_trip_extension_and_back() -> None:
    for mime in (
        "image/png",
        "image/jpeg",
        "application/json",
        "application/pdf",
        "text/markdown",
    ):
        ext = extension_for(mime)
        assert ext is not None


def test_text_classification_for_real_world_types() -> None:
    assert is_text(parse("text/html"))
    assert is_text("application/atom+xml")
    assert not is_text("application/octet-stream")
