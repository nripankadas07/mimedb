"""Tests for category classification."""

from __future__ import annotations

import pytest

from mimedb import (
    ParsedMimeType,
    category,
    is_audio,
    is_image,
    is_text,
    is_video,
    parse,
)


@pytest.mark.parametrize(
    "mime, expected",
    [
        ("text/html", "text"),
        ("image/png", "image"),
        ("audio/mpeg", "audio"),
        ("video/mp4", "video"),
        ("application/json", "application"),
        ("font/woff2", "font"),
        ("model/gltf+json", "model"),
        ("multipart/form-data", "multipart"),
        ("message/rfc822", "message"),
        ("chemical/x-pdb", "chemical"),
        ("example/foo", "example"),
    ],
)
def test_category_for_known_top_level(mime: str, expected: str) -> None:
    assert category(mime) == expected


def test_category_for_unknown_top_level() -> None:
    # A custom top-level type that's not in the closed set.
    assert category("weird/custom") == "unknown"


def test_category_accepts_parsed() -> None:
    parsed = parse("image/png")
    assert category(parsed) == "image"


class TestIsText:
    def test_text_subtypes(self) -> None:
        assert is_text("text/plain") is True
        assert is_text("text/html") is True

    def test_known_textlike_application(self) -> None:
        assert is_text("application/json") is True
        assert is_text("application/xml") is True
        assert is_text("application/yaml") is True
        assert is_text("application/javascript") is True

    def test_textlike_suffix(self) -> None:
        assert is_text("application/vnd.api+json") is True
        assert is_text("application/atom+xml") is True

    def test_binary_application(self) -> None:
        assert is_text("application/pdf") is False
        assert is_text("application/octet-stream") is False

    def test_image_is_not_text(self) -> None:
        assert is_text("image/png") is False

    def test_with_parsed_input(self) -> None:
        parsed = ParsedMimeType("text", "html")
        assert is_text(parsed) is True


class TestSpecificPredicates:
    def test_is_image(self) -> None:
        assert is_image("image/png") is True
        assert is_image("video/mp4") is False

    def test_is_audio(self) -> None:
        assert is_audio("audio/mpeg") is True
        assert is_audio("text/plain") is False

    def test_is_video(self) -> None:
        assert is_video("video/mp4") is True
        assert is_video("audio/mpeg") is False
