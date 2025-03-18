"""Read generation parameters from the newest InvokeAI metadata format."""

from __future__ import annotations

import json
from contextlib import suppress
from typing import Any, Dict, TYPE_CHECKING

from sd_parsers.data import Model, Prompt, Sampler, PromptInfo
from sd_parsers.exceptions import ParserError

from ._variant_dream import _get_sampler

if TYPE_CHECKING:
    from .parser import InvokeAIParser


def _parse_invokeai_meta(parser: InvokeAIParser, parameters: Dict[str, Any]) -> PromptInfo:
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
            sampler["prompts"] = [Prompt(value=prompt)]

    # negative prompt
    with suppress(KeyError):
        prompt = metadata.pop("negative_prompt")
        if prompt != "":
            sampler["negative_prompts"] = [Prompt(value=prompt)]

    # model
    with suppress(KeyError):
        model_info = metadata.pop("model")

        sampler["model"] = Model(
            name=model_info.pop("model_name"),
            metadata=model_info,
        )

    return PromptInfo(parser.generator, [Sampler(**sampler)], metadata, parameters)


__all__ = ["_parse_invokeai_meta"]
