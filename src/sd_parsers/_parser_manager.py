"""Provides the ParserManager class."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Type, Union

from PIL import Image

from .data import PromptInfo
from .exceptions import ParserError
from .parser import Parser
from .parsers import MANAGED_PARSERS

if TYPE_CHECKING:
    from pathlib import Path

    from _typeshed import SupportsRead

logger = logging.getLogger(__name__)


class ParserManager:
    """
    Provides a simple way of testing multiple parser modules against a given image.
    """

    def __init__(
        self,
        *,
        two_pass: bool = True,
        normalize_parameters: bool = True,
        managed_parsers: Optional[List[Type[Parser]]] = None,
    ):
        """
        Initializes a ParserManager object.

        Optional Parameters:
            two_pass: for PNG images, use `Image.info` before using `Image.text` as metadata source.
            normalize_parameters: Try to unify the parameter keys of the parser outputs.
            managed_parsers: A list of parsers to be managed.

        The performance effects of two-pass parsing depends on the given image files.
        If the image files are correctly formed and can be read with one of the supported parser modules,
        setting `two_pass` to `True` will considerably shorten the time needed to read the image parameters.
        """
        self.two_pass = two_pass
        self.managed_parsers: List[Parser] = [
            parser(normalize_parameters) for parser in managed_parsers or MANAGED_PARSERS
        ]

    def parse(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
    ) -> Optional[PromptInfo]:
        """
        Try to extract image generation parameters from the given image.

        Parameters:
            image: a PIL Image, filename, pathlib.Path object or a file object.

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` function:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """

        def _parse(image: Image.Image):
            for parser, parameters, parsing_context in self._read_parameters(image):
                try:
                    samplers, metadata = parser.parse(parameters, parsing_context)

                    return PromptInfo(parser, samplers, metadata)

                except ParserError as error:
                    logger.debug("error in %s parser: %s", parser.generator.value, error)
                    continue

            return None

        if isinstance(image, Image.Image):
            return _parse(image)

        with Image.open(image) as _image:
            return _parse(_image)

    def read_parameters(self, image: Image.Image):
        """Try to extract image generation parameters from the given image."""
        return next(iter(self._read_parameters(image)), None)

    def _read_parameters(self, image: Image.Image):
        # two_pass only makes sense with PNG images
        two_pass = image.format == "PNG" if self.two_pass else False

        for use_text in [False, True] if two_pass else [True]:
            for parser in self.managed_parsers:
                try:
                    parameters, parsing_context = parser.read_parameters(image, use_text)
                    yield parser, parameters, parsing_context

                except ParserError as error:
                    logger.debug("error in %s parser: %s", parser.generator.value, error)
                    continue
