"""Provides the ParserManager class."""

from __future__ import annotations

import itertools
import logging
from contextlib import contextmanager
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Type, Union

from PIL import Image

from .data import PromptInfo
from .exceptions import ParserError
from .parser import Parser
from .parsers import MANAGED_PARSERS
from .extractors import METADATA_EXTRACTORS

if TYPE_CHECKING:
    from pathlib import Path

    from _typeshed import SupportsRead

logger = logging.getLogger(__name__)


class Eagerness(Enum):
    FAST = 1
    DEFAULT = 2
    EAGER = None


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
        debug: bool = False,
    ):
        """
        Initializes a ParserManager object.

        Optional Parameters:
            normalize_parameters: Try to unify the parameter keys of the parser outputs.
            managed_parsers: A list of parsers to be managed.

        """
        self._debug = debug

        self.managed_parsers: List[Parser] = [
            parser(normalize_parameters) for parser in managed_parsers or MANAGED_PARSERS
        ]

    def parse(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
        eagerness: Eagerness = Eagerness.DEFAULT,
    ) -> Optional[PromptInfo]:
        """
        Try to extract image generation parameters from the given image.

        Parameters:
            image: a PIL Image, filename, pathlib.Path object or a file object.
            eagerness: metadata searching effort
              FAST: cut some corners to save some time
              DEFAULT: try to ensure all metadata is read (default)
              EAGER: include additional methods to try and retrieve metadata (computationally expensive)

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` method:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """

        with _get_image(image) as image:
            if image.format is None:
                return None

            try:
                extractors = METADATA_EXTRACTORS[image.format][: eagerness.value]
            except KeyError:
                return None

            for get_metadata in itertools.chain(*extractors):
                for parser in self.managed_parsers:
                    try:
                        parameters = get_metadata(image, parser.generator)
                        if parameters is None:
                            continue

                        generator, samplers, metadata = parser.parse(parameters)
                        return PromptInfo(generator, samplers, metadata, parameters)
                    except ParserError as error:
                        if self._debug:
                            logger.debug("error in parser[%s]: %s", type(parser), error)

        return None
