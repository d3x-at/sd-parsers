"""Provides the ParserManager class."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, List, Optional, Type, Union

from PIL import Image

from .data import PromptInfo
from .exceptions import MetadataError, ParserError
from .parsers import Parser, MANAGED_PARSERS
from .extractors import METADATA_EXTRACTORS, Eagerness

if TYPE_CHECKING:
    from pathlib import Path

    from _typeshed import SupportsRead

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
        debug: bool = False,
        eagerness: Eagerness = Eagerness.DEFAULT,
        managed_parsers: Optional[List[Type[Parser]]] = None,
        normalize_parameters: bool = True,
    ):
        """
        Initializes a ParserManager object.

        Optional Parameters:
            normalize_parameters: Try to unify the parameter keys of the parser outputs.
            managed_parsers: A list of parsers to be managed.
            debug: Produce log messages when errors occur
            eagerness: metadata searching effort
             - FAST: cut some corners to save some time
             - DEFAULT: try to ensure all metadata is read (default)
             - EAGER: include additional methods to try and retrieve metadata (computationally expensive!)
        """
        self._eagerness = eagerness
        self._debug = debug

        self.managed_parsers: List[Parser] = [
            parser(normalize_parameters=normalize_parameters, debug=debug)
            for parser in managed_parsers or MANAGED_PARSERS
        ]

    def parse(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
        eagerness: Optional[Eagerness] = None,
    ) -> Optional[PromptInfo]:
        """
        Try to extract image generation parameters from the given image.

        Parameters:
            image: a PIL Image, filename, pathlib.Path object or a file object.
            eagerness: metadata searching effort (overrides ParserManager default)
             - FAST: cut some corners to save some time
             - DEFAULT: try to ensure all metadata is read
             - EAGER: include additional methods to try and retrieve metadata (computationally expensive!)

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` method:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """

        # use specific eagerness when given, otherwise use ParserManager's default
        eagerness = eagerness or self._eagerness

        def get_extractors(image: Image.Image):
            if image.format is None:
                if self._debug:
                    logger.debug("unknown image format")
                return

            try:
                extractors = METADATA_EXTRACTORS[image.format]
            except KeyError:
                if self._debug:
                    logger.debug("unsupported image format: %s", image.format)
                return

            for e in Eagerness:
                if e.value > eagerness.value:
                    break

                if e not in extractors:
                    continue

                for get_metadata in extractors[e]:
                    yield get_metadata

        with _get_image(image) as image:
            for get_metadata in get_extractors(image):
                for parser in self.managed_parsers:
                    try:
                        parameters = get_metadata(image, parser.generator)
                    except MetadataError:
                        if self._debug:
                            logger.exception("error reading metadata")
                        break

                    if parameters is None:
                        continue

                    try:
                        return parser.parse(parameters)
                    except ParserError as error:
                        if self._debug:
                            logger.error("error in parser[%s]: %s", type(parser), error)

        return None
