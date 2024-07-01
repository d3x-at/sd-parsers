"""Provides the ParserManager class."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, List, Optional, Type, Union

from PIL import Image

from .data import PromptInfo
from .exceptions import ParserError
from .parser import Parser
from .parsers import MANAGED_PARSERS

if TYPE_CHECKING:
    from pathlib import Path

    from _typeshed import SupportsRead, SupportsRichComparison

logger = logging.getLogger(__name__)


@contextmanager
def _get_image(image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image]):
    if isinstance(image, Image.Image):
        yield image
    else:
        with Image.open(image) as _image:
            yield _image


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
        underlying `Image.open()` method:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """

        with _get_image(image) as image:
            for parser, parameters, parsing_context in self._read_parameters(image):
                try:
                    samplers, metadata = parser.parse(parameters, parsing_context)

                    return PromptInfo(parser, samplers, metadata)

                except ParserError as error:
                    logger.debug("error in %s parser: %s", parser.generator.value, error)

        return None

    def read_parameters(self, image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image]):
        """
        Try to read image metadata from the given image that refers to generation parameters.

        Warning: This method is prone to returning false positives when given images that contain
        random metadata.

        Parameters:
            image: a PIL Image, filename, pathlib.Path object or a file object.

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` method:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """
        
        with _get_image(image) as image:
            try:
                parser, parameters, _ = next(
                    iter(self._read_parameters(image, lambda x: x._COMPLEXITY_INDEX))
                )
                return parser.generator, parameters

            except StopIteration:
                return None

    def _read_parameters(
        self,
        image: Image.Image,
        key: Optional[Callable[[Parser], SupportsRichComparison]] = None,
    ):
        # two_pass only makes sense with PNG images
        two_pass = image.format == "PNG" if self.two_pass else False

        for use_text in [False, True] if two_pass else [True]:
            for parser in sorted(self.managed_parsers, key=key) if key else self.managed_parsers:
                try:
                    parameters, parsing_context = parser.read_parameters(image, use_text)
                    yield parser, parameters, parsing_context

                except ParserError as error:
                    logger.debug("error in %s parser: %s", parser.generator.value, error)
