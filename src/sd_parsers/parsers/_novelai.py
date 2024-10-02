"""Parser for images generated by NovelAI or similar."""

import copy
import json
import re
from contextlib import suppress
from typing import Any, Callable, Dict

from PIL.Image import Image

from sd_parsers.data import Generators, Model, Prompt, Sampler
from sd_parsers.exceptions import MetadataError, ParserError
from sd_parsers.parser import Parser, ParseResult, ReplacementRules, pop_keys

SAMPLER_PARAMS = ["seed", "strength", "noise", "scale"]
REPLACEMENT_RULES: ReplacementRules = [("scale", "cfg_scale")]


class NovelAIParser(Parser):
    """parser for images generated by NovelAI"""

    def read_parameters(
        self,
        image: Image,
        get_png_metadata: Callable[[Image], Dict[str, Any]] | None = None,
    ):
        if image.format != "PNG":
            raise MetadataError("unsupported image format", image.format)

        metadata = get_png_metadata(image) if get_png_metadata else image.info
        try:
            description = metadata["Description"]
            software = metadata["Software"]
            source = metadata["Source"]
            comment = json.loads(metadata["Comment"])
        except Exception as error:
            raise MetadataError("no matching metadata") from error

        if software != "NovelAI":
            raise MetadataError("unknown software version", software)

        parameters = {
            "Comment": comment,
            "Description": description,
            "Software": software,
            "Source": source,
        }

        return parameters, None

    def parse(self, parameters: Dict[str, Any], _) -> ParseResult:
        try:
            metadata = copy.deepcopy(parameters["Comment"])
            params = parameters["Description"]
            source = parameters["Source"]
        except KeyError as error:
            raise ParserError("error reading parameter values") from error

        try:
            sampler = {
                "name": metadata.pop("sampler"),
                "parameters": self.normalize_parameters(
                    pop_keys(SAMPLER_PARAMS, metadata), REPLACEMENT_RULES
                ),
            }
        except KeyError as error:
            raise ParserError("no sampler found") from error

        sampler["prompts"] = [Prompt(1, params.strip())]

        with suppress(KeyError):
            sampler["negative_prompts"] = [Prompt(1, metadata.pop("uc"))]

        # model
        match = re.fullmatch(r"^(.*?)\s+([A-Z0-9]+)$", source)
        if match:
            model_name, model_hash = match.groups()
            sampler["model"] = Model(name=model_name, hash=model_hash)

        return Generators.NOVELAI, [Sampler(**sampler)], metadata
