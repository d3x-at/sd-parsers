"""Parser for images generated by InvokeAI."""
from __future__ import annotations

import copy
import json
import re
from contextlib import suppress
from enum import Enum
from typing import Any, Callable, Dict, List, NamedTuple

from PIL.Image import Image

from .._models import Model, Prompt, Sampler
from .._parser import Generators, Parser, ParseResult, ReplacementRules, pop_keys
from .._prompt_info import PromptInfo
from ..exceptions import ParserError

SAMPLER_PARAMS = ["cfg_scale", "cfg_rescale_multiplier", "perlin", "seed", "steps", "threshold"]

REPLACEMENT_RULES: ReplacementRules = [("size", (["width", "height"], "{width}x{height}"))]

DREAM_KEYS = {
    "A": ("sampler", None),
    "C": ("cfg_scale", float),
    "H": ("height", int),
    "s": ("steps", int),
    "S": ("seed", int),
    "W": ("width", int),
}

RE_PROMPT_NEGATIVES = re.compile(r"\[([^\[]*)\]")


class InvokeVariant(str, Enum):
    """InvokeAI metadata variants"""

    IMETA = "invokeai_metadata"
    SDMETA = "sd-metadata"
    DREAM = "Dream"


class InvokeAIParser(Parser):
    """parser for images generated by invokeai"""

    @property
    def generator(self):
        return Generators.INVOKEAI

    def read_parameters(self, image: Image, use_text: bool = True):
        if image.format != "PNG":
            return None

        image_info = image.text if use_text else image.info  # type: ignore
        for variant in InvokeVariant:
            try:
                metadata = image_info[variant.value]
            except KeyError:
                continue

            if VARIANT_PARSERS[variant].decode_json:
                try:
                    metadata = json.loads(metadata)
                except (TypeError, json.JSONDecodeError) as error:
                    raise ParserError("error reading metadata") from error

            return PromptInfo(self, parsing_context=variant, parameters={variant.value: metadata})

        return None

    def parse(self, parameters: Dict[str, Any], parsing_context: InvokeVariant) -> ParseResult:
        try:
            metadata = copy.deepcopy(parameters[parsing_context.value])
        except KeyError as error:
            raise ParserError("error reading parameter string") from error

        samplers, metadata = VARIANT_PARSERS[parsing_context].parse(self, metadata)

        return samplers, metadata


def _parse_invokeai_meta(parser: Parser, metadata: Dict[str, Any]):
    """Read generation parameters from the newest InvokeAI metadata format."""

    # sampler
    sampler = _get_sampler(parser, metadata, "scheduler")

    # positive prompt
    with suppress(KeyError):
        sampler.prompts.append(Prompt(value=metadata.pop("positive_prompt")))

    # negative prompt
    with suppress(KeyError):
        sampler.negative_prompts.append(Prompt(value=metadata.pop("negative_prompt")))

    # model
    with suppress(KeyError):
        model_info = metadata.pop("model")

        sampler.model = Model(
            name=model_info.pop("model_name"),
            parameters=model_info,
        )

    return [sampler], parser.normalize_parameters(metadata, REPLACEMENT_RULES, False)


def _parse_sd_metadata(parser: Parser, metadata: Dict[str, Any]):
    """Read generation parameters for an image containing a `sd-metadata` field."""

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

    for prompt_item in prompts:
        prompt_weight = prompt_item.get("weight", None)
        prompt_params = {} if prompt_weight is None else {"weight": prompt_weight}
        with suppress(KeyError):
            _add_prompts(sampler, prompt_item["prompt"], prompt_params)

    # model
    model_name = metadata.pop("model_weights", None)
    model_hash = metadata.pop("model_hash", None)
    if model_name or model_hash:
        sampler.model = Model(name=model_name, model_hash=model_hash)

    metadata = parser.normalize_parameters({**metadata, **metadata_image}, REPLACEMENT_RULES)

    return [sampler], metadata


def _parse_dream(parser: Parser, _metadata: str):
    """Read generation parameters from images generated by legacy InvokeAI."""

    match = re.match(r'^"(.*?)"(.*)$', _metadata)
    if match is None:
        raise ParserError("could not read generation parameters")

    prompts, args = match.groups()

    # split args into metadata
    metadata = {}
    end = 0
    for match in re.finditer(r"\s+-(\w+)\s+([^\s]+)", args):
        key, value = match.groups()

        try:
            key_name, convert = DREAM_KEYS[key]
            metadata[key_name] = convert(value) if convert else value
        except (KeyError, ValueError):
            metadata[key] = value

        end = match.end(0)

    _ = args[end:].strip()  # TODO: decide what to do with the remainder data

    # sampler
    sampler = _get_sampler(parser, metadata, "sampler")

    # prompts
    _add_prompts(sampler, prompts, {})

    return [sampler], parser.normalize_parameters(metadata, REPLACEMENT_RULES, False)


def _get_sampler(parser: Parser, metadata: Dict[str, Any], key: str):
    try:
        return Sampler(
            name=metadata.pop(key),
            parameters=parser.normalize_parameters(
                pop_keys(SAMPLER_PARAMS, metadata), REPLACEMENT_RULES
            ),
        )
    except KeyError as error:
        raise ParserError("no sampler found") from error


def _add_prompts(sampler: Sampler, combined_prompt: str, parameters: dict):
    for negative_prompt in RE_PROMPT_NEGATIVES.findall(combined_prompt):
        prompt = Prompt(value=negative_prompt, parameters=parameters)
        sampler.negative_prompts.append(prompt)

    positive_prompt = RE_PROMPT_NEGATIVES.sub("", combined_prompt).strip()
    prompt = Prompt(value=positive_prompt, parameters=parameters)
    sampler.prompts.append(prompt)


class VariantParser(NamedTuple):
    """Holds a parsing function for a metadata format and
    information on how to prepare the data passed to it."""

    parse: Callable[[Parser, Any], tuple[List[Sampler], Dict[str, Any]]]
    decode_json: bool


VARIANT_PARSERS = {
    InvokeVariant.SDMETA: VariantParser(_parse_sd_metadata, True),
    InvokeVariant.IMETA: VariantParser(_parse_invokeai_meta, True),
    InvokeVariant.DREAM: VariantParser(_parse_dream, False),
}
