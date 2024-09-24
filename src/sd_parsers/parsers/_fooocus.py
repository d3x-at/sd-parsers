"""Parser for images generated by AUTOMATIC1111's stable-diffusion-webui or similar."""

import copy
import json
from typing import Any, Dict

from PIL.Image import Image

from sd_parsers.data import Generators, Model, Prompt, Sampler
from sd_parsers.exceptions import MetadataError, ParserError
from sd_parsers.parser import Parser, ParseResult, ReplacementRules, get_exif_value, pop_keys

SAMPLER_PARAMS = ["guidance_scale", "scheduler", "seed", "sharpness", "steps"]

REPLACEMENT_RULES: ReplacementRules = [("guidance_scale", "cfg_scale")]


class FooocusParser(Parser):
    """Parse images generated by Foocus."""

    _COMPLEXITY_INDEX = 90

    def read_parameters(self, image: Image, use_text: bool = True):
        try:
            if image.format == "PNG":
                parameters = image.text["parameters"] if use_text else image.info["parameters"]  # type: ignore
            elif image.format in ("JPEG", "WEBP"):
                parameters = get_exif_value(image, "UserComment")
            else:
                raise MetadataError("unsupported image format", image.format)

            parameters = json.loads(parameters)
            version = parameters["version"]

        except Exception as error:
            raise MetadataError("no matching metadata") from error

        if not version.startswith("Fooocus "):
            raise MetadataError("unknown version string", version)

        return {"parameters": parameters}, None

    def parse(self, _parameters: Dict[str, Any], _) -> ParseResult:
        try:
            parameters = copy.deepcopy(_parameters["parameters"])

            model = Model(
                name=parameters.pop("base_model"),
                hash=parameters.pop("base_model_hash"),
            )

            sampler_parameters = self.normalize_parameters(
                pop_keys(SAMPLER_PARAMS, parameters),
                REPLACEMENT_RULES,
            )

            sampler = {
                "name": parameters.pop("sampler"),
                "parameters": sampler_parameters,
                "model": model,
                "prompts": [Prompt(1, parameters.pop("prompt"))],
            }

            negative_prompt = parameters.pop("negative_prompt")
            if negative_prompt:
                sampler["negative_prompts"] = [Prompt(1, negative_prompt)]

        except KeyError as error:
            raise ParserError("error reading parameter value") from error

        return Generators.FOOOCUS, [Sampler(**sampler)], parameters
