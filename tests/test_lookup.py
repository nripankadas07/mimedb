"""Tests for the MIME ↔ extension lookup helpers."""

from __future__ import annotations

import pytest

from mimedb import (
    InvalidExtensionError,
    InvalidMimeTypeError,
    UnknownMimeTypeError,
    extension_for,
    extensions_for,
    iter_types,
    lookup,
    mime_for_extension,
    mime_for_filename,
    register,
    unregister,
)


class TestExtensionFor:
    def test_primary_extension(self) -> None:
        assert extension_for("image/png") == "png"
        assert extension_for("image/jpeg") == "jpg"
        assert extension_for("text/plain") == "txt"

    def test_case_insensitive(self) -> None:
        assert extension_for("IMAGE/PNG") == "png"

    def test_unknown_returns_none(self) -> None:
        assert extension_for("application/x-unknown") is None

    def test_invalid_input_raises(self) -> None:
        with pytest.raises(InvalidMimeTypeError):
            extension_for("")


class TestExtensionsFor:
    def test_returns_all_extensions(self) -> None:
        extensions = extensions_for("image/jpeg")
        assert "jpg" in extensions and "jpeg" in extensions

    def test_returns_empty_list_for_unknown(self) -> None:
        assert extensions_for("application/x-unknown") == []

    def test_no_duplicates_in_combined_user_and_builtin(self) -> None:
        register("image/jpeg", ["jpg"])
        extensions = extensions_for("image/jpeg")
        assert extensions.count("jpg") == 1


class TestMimeForExtension:
    def test_basic_lookups(self) -> None:
        assert mime_for_extension("png") == "image/png"
        assert mime_for_extension("PDF") == "application/pdf"
        assert mime_for_extension("md") == "text/markdown"

    def test_with_leading_dot(self) -> None:
        assert mime_for_extension(".png") == "image/png"

    def test_case_insensitive(self) -> None:
        assert mime_for_extension("JPG") == "image/jpeg"

    def test_unknown_returns_none(self) -> None:
        assert mime_for_extension("xyzzy123") is None

    def test_non_string_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            mime_for_extension(123)  # type: ignore[arg-type]

    def test_empty_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            mime_for_extension("")

    def test_only_dot_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            mime_for_extension(".")


class TestMimeForFilename:
    def test_simple_filename(self) -> None:
        assert mime_for_filename("photo.png") == "image/png"

    def test_path_with_directories(self) -> None:
        assert mime_for_filename("/var/data/notes.md") == "text/markdown"

    def test_multiple_dots_uses_last(self) -> None:
        assert mime_for_filename("archive.tar.gz") == "application/gzip"

    def test_no_extension_returns_none(self) -> None:
        assert mime_for_filename("README") is None

    def test_unknown_extension_returns_none(self) -> None:
        assert mime_for_filename("data.xyzzy123") is None

    def test_empty_string_returns_none(self) -> None:
        assert mime_for_filename("") is None

    def test_directory_only_returns_none(self) -> None:
        assert mime_for_filename("foo/") is None

    def test_non_string_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            mime_for_filename(123)  # type: ignore[arg-type]


class TestLookup:
    def test_known_mime_returns_tuple(self) -> None:
        assert lookup("image/png") == ("png",)

    def test_unknown_raises(self) -> None:
        with pytest.raises(UnknownMimeTypeError):
            lookup("application/x-unknown")


class TestIterTypes:
    def test_yields_known_types(self) -> None:
        names = list(iter_types())
        assert "image/png" in names
        assert "application/json" in names

    def test_includes_user_registered(self) -> None:
        register("application/x-custom", ["xcst"])
        assert "application/x-custom" in list(iter_types())


class TestRegisterUnregister:
    def test_register_then_lookup(self) -> None:
        register("application/x-custom", ["xcst"])
        assert mime_for_extension("xcst") == "application/x-custom"
        assert extension_for("application/x-custom") == "xcst"

    def test_register_with_dot_prefix_ok(self) -> None:
        register("application/x-other", [".xothr"])
        assert mime_for_extension("xothr") == "application/x-other"

    def test_register_empty_extensions_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            register("application/x-empty", [])

    def test_register_non_string_extension_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            register("application/x-nope", [123])  # type: ignore[list-item]

    def test_register_only_dot_raises(self) -> None:
        with pytest.raises(InvalidExtensionError):
            register("application/x-bad", ["."])

    def test_register_then_unregister_round_trip(self) -> None:
        register("application/x-tmp", ["xtmp"])
        assert unregister("application/x-tmp") is True
        assert mime_for_extension("xtmp") is None

    def test_unregister_unknown_returns_false(self) -> None:
        assert unregister("application/x-never-registered") is False

    def test_user_registration_takes_priority_in_lookup(self) -> None:
        register("application/x-priority", ["prio"])
        register("application/x-other", ["prio"])
        # First registration wins (setdefault semantics).
        assert mime_for_extension("prio") == "application/x-priority"


class TestEdgeCoverage:
    def test_iter_types_dedupes_overlap(self) -> None:
        # Registering an existing built-in should not double-count it.
        register("image/png", ["pngx"])
        names = list(iter_types())
        assert names.count("image/png") == 1

    def test_unregister_skips_extensions_owned_by_other(self) -> None:
        # Two MIME types claim the same extension; first one wins via
        # setdefault. Unregistering the second must NOT remove the
        # extension entry, because it's owned by the first.
        register("application/x-first", ["sharedext"])
        register("application/x-second", ["sharedext"])
        assert mime_for_extension("sharedext") == "application/x-first"
        # unregister the second; first should still own the extension.
        assert unregister("application/x-second") is True
        assert mime_for_extension("sharedext") == "application/x-first"
