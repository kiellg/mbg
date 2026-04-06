"""This module defines the in-memory database for storing review data."""

from typing import Any, Dict

_REVIEW_DB: Dict[str, Dict[str, Any]] = {}
