"""Shared test fixtures for mimedb."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(autouse=True)
def reset_runtime_registry() -> None:
    """Clear any user-registered entries between tests."""
    from mimedb import _lookup

    _lookup._USER_EXTENSIONS_BY_MIME.clear()
    _lookup._USER_MIME_BY_EXTENSION.clear()
