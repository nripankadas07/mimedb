"""Tests for the parse / format pipeline."""

from __future__ import annotations

import pytest

from mimedb import (
    InvalidMimeTypeError,
    ParsedMimeType,
    format_mime,
    parse,
)


class TestParseHappyPath:
    def test_parses_simple_type(self) -> None:
        parsed = parse("text/plain")
        assert parsed.type_ == "text"
        assert parsed.subtype == "plain"
        assert parsed.suffix is None
        assert dict(parsed.parameters) == {}

    def test_lower_cases_type_and_subtype(self) -> None:
        parsed = parse("Image/PNG")
        assert parsed.type_ == "image"
        assert parsed.subtype == "png"

    def test_strips_outer_whitespace(self) -> None:
        parsed = parse("  application/json  ")
        assert parsed.essence == "application/json"

    def test_extracts_suffix(self) -> None:
        parsed = parse("application/vnd.api+json")
        assert parsed.subtype == "vnd.api"
        assert parsed.suffix == "json"
        assert parsed.base == "application/vnd.api+json"

    def test_extracts_parameters(self) -> None:
        parsed = parse("text/html; charset=utf-8")
        assert parsed.parameters == {"charset": "utf-8"}

    def test_quoted_parameter_values_are_unwrapped(self) -> None:
        parsed = parse('multipart/form-data; boundary="abc 123"')
        assert parsed.parameters["boundary"] == "abc 123"

    def test_multiple_parameters(self) -> None:
        parsed = parse("text/plain; charset=utf-8; foo=bar")
        assert parsed.parameters == {"charset": "utf-8", "foo": "bar"}


class TestParseValidation:
    def test_non_string_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse(123)  # type: ignore[arg-type]

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("   ")

    def test_missing_slash_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("text")

    def test_empty_type_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("/plain")

    def test_empty_subtype_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("text/")

    def test_invalid_token_chars_raise(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("text/p lain")

    def test_dangling_plus_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("application/+json")

    def test_trailing_plus_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("application/foo+")

    def test_parameter_without_equals_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("text/html; charset")

    def test_parameter_empty_value_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("text/html; charset=")

    def test_parameter_invalid_name_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            parse("text/html; bad name=v")


class TestFormat:
    def test_round_trips_simple(self) -> None:
        parsed = parse("text/plain")
        assert format_mime(parsed) == "text/plain"

    def test_round_trips_with_suffix(self) -> None:
        parsed = parse("application/vnd.api+json")
        assert format_mime(parsed) == "application/vnd.api+json"

    def test_round_trips_with_parameters(self) -> None:
        parsed = parse("text/html; charset=utf-8")
        assert format_mime(parsed) == "text/html; charset=utf-8"

    def test_format_a_handcrafted_dataclass(self) -> None:
        parsed = ParsedMimeType("image", "svg", suffix="xml")
        assert format_mime(parsed) == "image/svg+xml"
