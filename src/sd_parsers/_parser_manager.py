"""Provides the ParserManager class."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

from PIL import Image

from .data import PromptInfo, Generators
from .exceptions import ParserError
from .parser import Parser
from .parsers import MANAGED_PARSERS

if TYPE_CHECKING:
    from pathlib import Path

    from _typeshed import SupportsRead, SupportsRichComparison

logger = logging.getLogger(__name__)

METADATA_EXTRACTORS: Dict[str, List[Callable[[Image.Image, Generators], Dict[str, Any]]]] = {
    "PNG": [
        # use image.info
        lambda i, _: i.info,
        # use image.text property (iTxt, tEXt and zTXt chunks may appear at the end of the file)
        lambda i, _: i.text,  # type: ignore
    ]
}
"""A list of retrieval functions to provide multiple metadata entrypoints for each parser module."""


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
        normalize_parameters: bool = True,
        managed_parsers: Optional[List[Type[Parser]]] = None,
    ):
        """
        Initializes a ParserManager object.

        Optional Parameters:
            normalize_parameters: Try to unify the parameter keys of the parser outputs.
            managed_parsers: A list of parsers to be managed.

        """
        self.managed_parsers: List[Parser] = [
            parser(normalize_parameters) for parser in managed_parsers or MANAGED_PARSERS
        ]

    def parse(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
        eagerness: int = 2,
    ) -> Optional[PromptInfo]:
        """
        Try to extract image generation parameters from the given image.

        Parameters:
            image: a PIL Image, filename, pathlib.Path object or a file object.
            eagerness: metadata searching effort
              1: cut some corners to save some time
              2: try to ensure all metadata is read (default)

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` method:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """
        if not 0 < eagerness <= 2:
            raise ValueError("depth not in valid range")

        for parser, parameters, parsing_context in self._read_parameters(image, eagerness):
            try:
                generator, samplers, metadata = parser.parse(parameters, parsing_context)
                return PromptInfo(generator, samplers, metadata, parameters)
            except ParserError as error:
                logger.debug("error in parser: %s", error)

        return None

    def _read_parameters(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
        max_tries: int,
        key: Optional[Callable[[Parser], SupportsRichComparison]] = None,
    ):
        with _get_image(image) as image:
            if image.format is None:
                raise ParserError("unknown image format")

            extractors = METADATA_EXTRACTORS.get(image.format, [None])

            for get_metadata in extractors[:max_tries]:
                for parser in (
                    sorted(self.managed_parsers, key=key) if key else self.managed_parsers
                ):
                    try:
                        parameters, parsing_context = parser.read_parameters(image, get_metadata)
                        yield parser, parameters, parsing_context

                    except ParserError as error:
                        logger.debug("error in parser: %s", error)
