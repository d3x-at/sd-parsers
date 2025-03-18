"""Parser for images generated by NovelAI or similar."""

import json
import re
from contextlib import suppress
from typing import Any, Dict

from sd_parsers.data import Generators, Model, Prompt, Sampler, PromptInfo
from sd_parsers.exceptions import ParserError
from sd_parsers.parser import Parser, ReplacementRules, pop_keys

SAMPLER_PARAMS = ["seed", "strength", "noise", "scale"]
REPLACEMENT_RULES: ReplacementRules = [("scale", "cfg_scale")]


class NovelAIParser(Parser):
    """parser for images generated by NovelAI"""

    generator = Generators.NOVELAI

    def parse(self, parameters: Dict[str, Any]) -> PromptInfo:
        try:
            metadata = json.loads(parameters["Comment"])
            params = parameters["Description"]
            source = parameters["Source"]
        except Exception as error:
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

        sampler["prompts"] = [Prompt(params.strip())]

        with suppress(KeyError):
            sampler["negative_prompts"] = [Prompt(metadata.pop("uc"))]

        # model
        match = re.fullmatch(r"^(.*?)\s+([A-Z0-9]+)$", source)
        if match:
            model_name, model_hash = match.groups()
            sampler["model"] = Model(name=model_name, hash=model_hash)

        return PromptInfo(self.generator, [Sampler(**sampler)], metadata, parameters)
