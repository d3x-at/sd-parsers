"""Parser for images generated by InvokeAI."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, NamedTuple


from sd_parsers.data import Generators, PromptInfo
from sd_parsers.exceptions import ParserError

from .._parser import Parser

from ._variant_dream import _parse_dream
from ._variant_invokeai_meta import _parse_invokeai_meta
from ._variant_sd_metadata import _parse_sd_metadata

logger = logging.getLogger(__name__)


class VariantParser(NamedTuple):
    """Holds a parsing function for a metadata format and
    information on how to prepare the data passed to it."""

    parse: Callable[[InvokeAIParser, Any], PromptInfo]
    read_parameters: Callable[[dict], dict]


VARIANT_PARSERS = [
    VariantParser(
        _parse_sd_metadata,
        lambda m: {"sd-metadata": m["sd-metadata"]},
    ),
    VariantParser(
        _parse_dream,
        lambda m: {"Dream": m["Dream"]},
    ),
    VariantParser(
        _parse_invokeai_meta,
        lambda m: {
            key: m[key] for key in {"invokeai_metadata", "invokeai_graph"}.intersection(m.keys())
        },
    ),
]


class InvokeAIParser(Parser):
    """parser for images generated by invokeai"""

    generator = Generators.INVOKEAI

    def parse(self, metadata: Dict[str, Any]) -> PromptInfo:
        for variant in VARIANT_PARSERS:
            try:
                parameters = variant.read_parameters(metadata)
                return variant.parse(self, parameters)
            except KeyError:
                continue

        raise ParserError("no sampler found")
