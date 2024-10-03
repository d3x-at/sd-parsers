"""Parser for images generated by AUTOMATIC1111's stable-diffusion-webui or similar."""

import json
import re
from contextlib import suppress
from typing import Any, Callable, Dict, Optional

from PIL.Image import Image

from sd_parsers.data import Generators, Model, Prompt, Sampler
from sd_parsers.exceptions import MetadataError, ParserError
from sd_parsers.parser import Parser, ParseResult, ReplacementRules, get_exif_value, pop_keys

SAMPLER_PARAMS = ["Sampler", "CFG scale", "Seed", "Steps", "ENSD", "Schedule type"]

REPLACEMENT_RULES: ReplacementRules = [("Schedule type", "scheduler")]


class AUTOMATIC1111Parser(Parser):
    """parse images created in AUTOMATIC1111's webui"""

    _COMPLEXITY_INDEX = 100

    def read_parameters(
        self,
        image: Image,
        get_metadata: Optional[Callable[[Image], Dict[str, Any]]] = None,
    ):
        try:
            if image.format == "PNG":
                metadata = get_metadata(image) if get_metadata else image.info
                parameters = metadata["parameters"]
            elif image.format in ("JPEG", "WEBP"):
                parameters = get_exif_value(image, "UserComment")
            else:
                raise MetadataError("unsupported image format", image.format)

        except (KeyError, ValueError) as error:
            raise MetadataError("no matching metadata") from error

        return {"parameters": parameters}, None

    def parse(self, parameters: Dict[str, Any], _) -> ParseResult:
        try:
            lines = parameters["parameters"].split("\n")
        except (KeyError, ValueError) as error:
            raise ParserError("error reading parameter string") from error

        info_index, sampler_info, metadata = get_sampler_info(lines)
        prompts = "\n".join(lines[:info_index]).split("Negative prompt:")
        prompt, negative_prompt = map(str.strip, prompts + [""] * (2 - len(prompts)))

        try:
            sampler = {
                "name": sampler_info.pop("Sampler"),
                "parameters": self.normalize_parameters(sampler_info, REPLACEMENT_RULES),
            }
        except KeyError as error:
            raise ParserError("no sampler found") from error

        model_name = metadata.pop("Model", None)
        model_hash = metadata.pop("Model hash", None)

        if model_name or model_hash:
            sampler["model"] = Model(
                name=model_name,
                hash=model_hash,
            )

        if prompt:
            sampler["prompts"] = [Prompt(1, prompt)]

        if negative_prompt:
            sampler["negative_prompts"] = [Prompt(1, negative_prompt)]

        return Generators.AUTOMATIC1111, [Sampler(**sampler)], metadata


def get_sampler_info(lines):
    def split_meta(line: str) -> Dict[str, str]:
        # try to extract civitai hashes
        civitai_hashes = None
        match = re.search(r"(?:,\s*)?Hashes:\s*(\{[^\}]*\})\s*", line)
        if match:
            with suppress(json.JSONDecodeError):
                civitai_hashes = json.loads(match.group(1))
            start, end = match.span(0)
            line = line[:start] + line[end:]

        metadata = {}
        for item in line.split(","):
            try:
                key, value = map(str.strip, item.split(":"))
                metadata[key] = value
            except ValueError:
                pass

        if civitai_hashes:
            metadata["civitai_hashes"] = civitai_hashes

        return metadata

    for index, line in reversed(list(enumerate(lines))):
        metadata = split_meta(line)
        sampler_info = dict(pop_keys(SAMPLER_PARAMS, metadata))
        if len(sampler_info) >= 3:
            return index, sampler_info, metadata

    raise ParserError("no sampler information found")
