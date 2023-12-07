"""Example stub for additional parsers"""
from typing import Any, Dict

from PIL.Image import Image

from .._parser import Generators, Parser, ParseResult
from .._prompt_info import PromptInfo
from ._managed_parsers import MANAGED_PARSERS  # noqa: F401


class DummyParser(Parser):
    """
    Example stub for additional parsers
    """

    @property
    def generator(self):
        return Generators.UNKNOWN

    def read_parameters(self, image: Image):
        """
        Read the relevant generation paramaters out of the given image.
        Keep this method as short as possible.

        - return [`None`, `exception`] when an exception is encountered.
        - return [`PromptInfo`, `None`] when the image data can be parsed.
        - else return [`None`, `None`]
        """
        return PromptInfo(self, parameters={"my_data": {}}), None

    def parse(self, parameters: Dict[str, Any]) -> ParseResult:
        """
        Process the generation parameters which were read from the image with `read_parameters`.
        """
        my_data = parameters["my_data"]
        return [], my_data


# MANAGED_PARSERS.append(DummyParser)
