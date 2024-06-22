"""Read generation parameters from images generated by legacy InvokeAI."""
from __future__ import annotations

import re
from contextlib import suppress
from typing import Any, Dict

from sd_parsers.data import Prompt, Sampler
from sd_parsers.exceptions import ParserError
from sd_parsers.parser import Parser, ParseResult, pop_keys

SAMPLER_PARAMS = ["cfg_scale", "cfg_rescale_multiplier", "perlin", "seed", "steps", "threshold"]

DREAM_KEYS = {
    "A": ("sampler", None),
    "C": ("cfg_scale", float),
    "H": ("height", int),
    "s": ("steps", int),
    "S": ("seed", int),
    "W": ("width", int),
}


def _parse_dream(parser: Parser, parameters: dict) -> ParseResult:
    """Read generation parameters from images generated by legacy InvokeAI."""

    try:
        match = re.match(r'^"(.*?)"(.*)$', parameters["Dream"])
        if match is None:
            raise ParserError("could not read generation parameters")
    except KeyError as error:
        raise ParserError("Dream parameter not found") from error

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

    return [Sampler(**sampler)], metadata


def _get_sampler(parser: Parser, metadata: Dict[str, Any], key: str):
    try:
        samper_parameters = parser.normalize_parameters(pop_keys(SAMPLER_PARAMS, metadata))
        sampler_data = {
            "name": metadata.pop(key),
            "parameters": samper_parameters,
        }
    except KeyError as error:
        raise ParserError("no sampler found") from error

    return sampler_data


def _add_prompts(sampler: dict, combined_prompt: str, metadata: dict):
    prompts = []
    negative_prompts = []

    def _get_prompt(prompt_string: str):
        prompt_text = prompt_string.strip(" ,")
        if not prompt_text:
            raise ValueError
        return Prompt(value=prompt_text, metadata=metadata)

    prompt_index = 0
    for match in re.finditer(r"\[([^\[]*)\]", combined_prompt):
        with suppress(ValueError):
            negative_prompts.append(_get_prompt(match.group()[1:-1]))

        start, end = match.span()
        with suppress(ValueError):
            prompts.append(_get_prompt(combined_prompt[prompt_index:start]))
        prompt_index = end

    if prompt_index < len(combined_prompt):
        with suppress(ValueError):
            prompts.append(_get_prompt(combined_prompt[prompt_index:]))

    try:
        sampler["prompts"].extend(prompts)
    except KeyError:
        sampler["prompts"] = prompts

    try:
        sampler["negative_prompts"].extend(negative_prompts)
    except KeyError:
        sampler["negative_prompts"] = negative_prompts


__all__ = ["_parse_dream"]
