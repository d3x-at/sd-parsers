"""Read generation parameters for an image containing a `sd-metadata` field."""

from __future__ import annotations

import json
from typing import Any, Dict, TYPE_CHECKING

from sd_parsers.data import Model, Sampler, PromptInfo
from sd_parsers.exceptions import ParserError

from ._variant_dream import _add_prompts, _get_sampler

if TYPE_CHECKING:
    from .parser import InvokeAIParser


def _parse_sd_metadata(parser: InvokeAIParser, parameters: Dict[str, Any]) -> PromptInfo:
    """Read generation parameters for an image containing a `sd-metadata` field."""

    try:
        metadata = json.loads(parameters["sd-metadata"])
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ParserError("error reading metadata") from error

    try:
        metadata_image = metadata.pop("image")
    except KeyError as error:
        raise ParserError("no image entry found") from error

    # sampler
    sampler = _get_sampler(parser, metadata_image, "sampler")

    # prompts
    try:
        prompts = metadata_image.pop("prompt")
    except KeyError as error:
        raise ParserError("no prompt entry found") from error
    except AttributeError as error:
        raise ParserError("malformed prompt information") from error

    for prompt_item in prompts:
        try:
            prompt_text = prompt_item.pop("prompt")
            _add_prompts(sampler, prompt_text, prompt_item)
        except KeyError:
            continue
        except AttributeError as error:
            raise ParserError("malformed prompt information") from error

    # model
    model_name = metadata.pop("model_weights", None)
    model_hash = metadata.pop("model_hash", None)
    if model_name or model_hash:
        sampler["model"] = Model(name=model_name, hash=model_hash)

    return PromptInfo(
        parser.generator, [Sampler(**sampler)], {**metadata, **metadata_image}, parameters
    )


__all__ = ["_parse_sd_metadata"]
