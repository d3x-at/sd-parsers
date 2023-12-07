"""Parser for images generated by InvokeAI or similar."""
import json
import re
from contextlib import suppress
from typing import Any, Dict

from PIL.Image import Image
from PIL.PngImagePlugin import PngImageFile

from .._exceptions import ParserError
from .._models import Model, Prompt, Sampler
from .._parser import Generators, Parser, ParseResult, ReplacementRules, pop_keys
from .._prompt_info import PromptInfo
from ._managed_parsers import MANAGED_PARSERS

_RE_PROMPT_NEGATIVES = re.compile(r"\[([^\[]*)\]")

SAMPLER_PARAMS = ["cfg_scale", "perlin", "seed", "steps", "threshold"]
REPLACEMENT_RULES: ReplacementRules = [("size", (["width", "height"], "{width}x{height}"))]


class InvokeAIParser(Parser):
    """parser for images generated by invokeai"""

    @property
    def generator(self):
        return Generators.INVOKEAI

    def read_parameters(self, image: Image):
        if not isinstance(image, PngImageFile):
            return None, None

        try:
            parameters = {"sd-metadata": json.loads(image.text["sd-metadata"])}
        except (KeyError, json.JSONDecodeError, TypeError) as error:
            return None, error

        with suppress(KeyError):
            parameters["Dream"] = image.text["Dream"]

        return PromptInfo(self, parameters), None

    def parse(self, parameters: Dict[str, Any]) -> ParseResult:
        try:
            metadata = parameters["sd-metadata"]
            metadata_image = dict(metadata.pop("image"))
        except KeyError as error:
            raise ParserError("error reading prameter string") from error

        try:
            sampler = Sampler(
                name=metadata_image.pop("sampler"),
                parameters=self.normalize_parameters(
                    pop_keys(SAMPLER_PARAMS, metadata_image), REPLACEMENT_RULES
                ),
            )
        except KeyError as error:
            raise ParserError("no sampler found") from error

        try:
            for prompt_item in metadata_image.pop("prompt"):
                combined_prompt = prompt_item["prompt"]
                weight = prompt_item.get("weight", None)

                for negative_prompt in _RE_PROMPT_NEGATIVES.findall(combined_prompt):
                    sampler.negative_prompts.append(Prompt(value=negative_prompt, weight=weight))

                positive_prompt = _RE_PROMPT_NEGATIVES.sub("", combined_prompt).strip()
                sampler.prompts.append(Prompt(value=positive_prompt, weight=weight))

        except KeyError as error:
            raise ParserError("error getting prompt") from error

        model_name = metadata.pop("model_weights", None)
        model_hash = metadata.pop("model_hash", None)
        if model_name or model_hash:
            sampler.model = Model(
                name=model_name,
                model_hash=model_hash,
            )

        metadata = self.normalize_parameters({**metadata, **metadata_image}, REPLACEMENT_RULES)

        return [sampler], metadata


MANAGED_PARSERS.append(InvokeAIParser)