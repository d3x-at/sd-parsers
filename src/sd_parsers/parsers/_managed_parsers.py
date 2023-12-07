"""Provides a list of managed parsers."""
from typing import List, Type

from .._parser import Parser

MANAGED_PARSERS: List[Type[Parser]] = []
