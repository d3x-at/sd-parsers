"""Example stub for additional parsers"""
import copy
from typing import Any, Dict

from PIL.Image import Image

from sd_parsers.data import Generators, Sampler
from sd_parsers.parser import Parser, ParseResult


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

        If image is PNG:
        Use `image.text` as parameters source if use_text is True.
        Use `image.info` otherwise.

        - raise a ParserError when an exception is encountered.
        - return `PromptInfo when the image data can be parsed.
        - else return `None`

        Add a `parsing_context` to PromptInfo if you need to
        pass on processing information to the `parse()` method.
        """
        return {"my_data": {"key": "value"}}, None

    def parse(self, parameters: Dict[str, Any], parsing_context: Any) -> ParseResult:
        """
        Process the generation parameters which were read from the image with `read_parameters`.

        Make sure that the original parameters dict does not get altered in the process of parsing.
        If necessary, make a copy of the original parameters first.

        Raise a `ParserError` when something goes wrong while parsing the image parameters.
        """
        my_data = copy.deepcopy(parameters["my_data"])

        return [Sampler(name="some sampler", parameters={})], my_data
