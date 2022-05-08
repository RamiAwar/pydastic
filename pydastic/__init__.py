# type: ignore[attr-defined]
"""Pydastic is an elasticsearch python ORM based on Pydantic."""

import sys

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

from pydastic.error import (
    InvalidElasticsearchResponse,
    InvalidModelError,
    NotFoundError,
)
from pydastic.model import ESModel
from pydastic.pydastic import PydasticClient, connect
from pydastic.session import Session

__all__ = [
    "ESModel",
    "Session",
    "NotFoundError",
    "InvalidModelError",
    "InvalidElasticsearchResponse",
    "PydasticClient",
    "connect",
]
