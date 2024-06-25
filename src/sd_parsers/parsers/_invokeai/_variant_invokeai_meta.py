"""Read generation parameters from the newest InvokeAI metadata format."""
from __future__ import annotations

import json
from contextlib import suppress
from typing import Any, Dict

from sd_parsers.data import Model, Prompt, Sampler
from sd_parsers.exceptions import ParserError
from sd_parsers.parser import Parser, ParseResult

from ._variant_dream import _get_sampler


def _parse_invokeai_meta(parser: Parser, parameters: Dict[str, Any]) -> ParseResult:
    """Read generation parameters from the newest InvokeAI metadata format."""

    try:
        metadata = json.loads(parameters["invokeai_metadata"])
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ParserError("error reading metadata") from error

    # sampler
    sampler = _get_sampler(parser, metadata, "scheduler")

    # positive prompt
    with suppress(KeyError):
        prompt = metadata.pop("positive_prompt")
        if prompt != "":
            sampler["prompts"] = [Prompt(prompt_id=1, value=prompt)]

    # negative prompt
    with suppress(KeyError):
        prompt = metadata.pop("negative_prompt")
        if prompt != "":
            sampler["negative_prompts"] = [Prompt(prompt_id=1, value=prompt)]

    # model
    with suppress(KeyError):
        model_info = metadata.pop("model")

        sampler["model"] = Model(
            name=model_info.pop("model_name"),
            metadata=model_info,
        )

    return [Sampler(**sampler)], metadata


__all__ = ["_parse_invokeai_meta"]
