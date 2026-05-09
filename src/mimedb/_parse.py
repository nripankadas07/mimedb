"""Parse and format MIME-type strings."""

from __future__ import annotations

from typing import Iterable

from ._errors import InvalidMimeTypeError
from ._types import ParsedMimeType

# RFC 7231 token characters, sufficient for type/subtype/parameter names.
_VALID_TOKEN_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    "!#$&^_-.+",
)


def parse(mime_type: str) -> ParsedMimeType:
    """Parse ``mime_type`` into a :class:`ParsedMimeType`."""
    if not isinstance(mime_type, str):
        raise InvalidMimeTypeError(
            f"mime_type must be str, got {type(mime_type).__name__}",
        )
    text = mime_type.strip()
    if not text:
        raise InvalidMimeTypeError("mime_type is empty")
    head, _, params_text = text.partition(";")
    type_, subtype, suffix = _split_essence(head.strip())
    parameters = _parse_parameters(params_text)
    return ParsedMimeType(
        type_=type_,
        subtype=subtype,
        suffix=suffix,
        parameters=parameters,
    )


def format_mime(parsed: ParsedMimeType) -> str:
    """Render ``parsed`` back into its canonical string form."""
    rendered = parsed.base
    extras = "".join(
        f"; {key}={value}" for key, value in parsed.parameters.items()
    )
    return rendered + extras


def _split_essence(head: str) -> tuple[str, str, str | None]:
    if "/" not in head:
        raise InvalidMimeTypeError(
            f"missing '/' in {head!r} (expected type/subtype)",
        )
    type_, subtype = head.split("/", 1)
    type_ = _require_token(type_, "type")
    subtype_lower = _require_token(subtype, "subtype")
    if "+" in subtype_lower:
        sub_part, _, suffix_part = subtype_lower.rpartition("+")
        if not sub_part or not suffix_part:
            raise InvalidMimeTypeError(
                f"invalid suffix in subtype {subtype!r}",
            )
        return type_, sub_part, suffix_part
    return type_, subtype_lower, None


def _require_token(value: str, label: str) -> str:
    lowered = value.lower()
    if not lowered:
        raise InvalidMimeTypeError(f"empty {label}")
    if not _is_token(lowered):
        raise InvalidMimeTypeError(
            f"invalid {label} {value!r} (non-token characters)",
        )
    return lowered


def _is_token(value: str) -> bool:
    return all(ch in _VALID_TOKEN_CHARS for ch in value)


def _parse_parameters(text: str) -> dict[str, str]:
    parts: Iterable[str] = (segment.strip() for segment in text.split(";"))
    parameters: dict[str, str] = {}
    for segment in parts:
        if not segment:
            continue
        key, value = _parse_single_parameter(segment)
        parameters[key] = value
    return parameters


def _parse_single_parameter(segment: str) -> tuple[str, str]:
    if "=" not in segment:
        raise InvalidMimeTypeError(
            f"parameter segment {segment!r} missing '='",
        )
    name, _, raw_value = segment.partition("=")
    key = _require_token(name.strip(), "parameter name")
    value = _normalise_parameter_value(raw_value.strip())
    return key, value


def _normalise_parameter_value(raw: str) -> str:
    if not raw:
        raise InvalidMimeTypeError("empty parameter value")
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]
    return raw
