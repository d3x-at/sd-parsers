"""Example stub for additional parsers"""
import json
from typing import Any, Dict

from PIL.Image import Image

from sd_parsers.data import Generators, Model, Prompt, Sampler
from sd_parsers.exceptions import MetadataError, ParserError
from sd_parsers.parser import Parser, ParseResult, get_exif_value


class DummyParser(Parser):
    """
    Example stub for additional parsers
    """

    @property
    def generator(self):
        return Generators.UNKNOWN

    def read_parameters(self, image: Image, use_text: bool = True):
        """
        Read the relevant generation parameters from the given image.

        Keep this method as short as possible.

        Raise a `MetadataError` when any error is encountered.
        """

        parameters = {}

        # Of course, the way this parsing context is used in this example
        # is overly complicated to illustrate it's possible use.
        #
        # Use a unique parameter keys and ommit context data where possible.
        parsing_context = {
            "description": "any type of information that the parse method might need"
        }

        try:
            if image.format in ("JPEG", "WEBP"):
                parameters["user_comment"] = get_exif_value(image, "UserComment")

                # put a hint for the available values into parsing context
                parsing_context["parameters_key"] = "user_comment"

            elif image.format == "PNG":
                # Use `image.text` as parameters source if use_text is True.
                # Use `image.info` otherwise.
                metadata = image.text if use_text else image.info  # type: ignore

                # deserialize parameters in json format
                parameters["some_image_parameter"] = json.loads(
                    metadata["this_parameter_in_json_format"]
                )

                # put a hint for the available values into parsing context
                parsing_context["parameters_key"] = "some_image_parameter"

            else:
                raise MetadataError("unsupported image format", image.format)

        except Exception as error:
            raise MetadataError("no matching metadata") from error

        return parameters, parsing_context

    def parse(self, parameters: Dict[str, Any], parsing_context: Any) -> ParseResult:
        """
        Process the generation parameters returned by `read_parameters()`.

        Make sure that the original parameters data does not get altered in the process of parsing.

        Raise a `ParserError` when something goes wrong.
        """

        parameters_key = parsing_context["parameters_key"]

        working_parameters = dict(parameters[parameters_key])

        try:
            sampler = {
                "name": working_parameters.pop("sampler name"),
                "parameters": "a dict of sampler-specific parameters, i.e.: cfg scale, seed, steps, ...",
                "model": Model("name of the used checkpoint", "hash value of the checkpoint"),
                "prompts": [
                    Prompt(1, "positive prompt"),
                ],
                "negative_prompts": [
                    Prompt(2, "negative prompt"),
                    Prompt(3, "try to keep prompt id's unique"),
                ],
            }
        except Exception as error:
            raise ParserError("something happened here") from error

        # return list of samplers and unused working parameters
        return [Sampler(**sampler)], working_parameters
