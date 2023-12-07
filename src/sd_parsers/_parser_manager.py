"""Provides the ParserManager class."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from PIL import Image

from ._exceptions import ParserError
from ._parser import Parser
from ._prompt_info import PromptInfo
from .parsers._managed_parsers import MANAGED_PARSERS

if TYPE_CHECKING:
    from pathlib import Path

    from _typeshed import SupportsRead


class ParserManager:
    """
    Provides a simple way of testing multiple parser modules against a given image.

    Attributes:
        managed_parsers (list[Parser]): The parsers managed by this ParserManager instance.
    """

    managed_parsers: List[Parser]
    """The parsers managed by this ParserManager instance."""

    def __init__(
        self,
        normalize_parameters: bool = True,
        managed_parsers: Optional[List[Parser]] = None,
    ):
        """
        Initializes a ParserManager object.

        Optional Parameters:
            normalize_parameters (bool): Try to unify the parameter keys of the parser outputs.
            managed_parsers (list[Parser]): A list of parsers to be managed.
        """
        if managed_parsers is not None:
            self.managed_parsers = managed_parsers
        else:
            self.managed_parsers = [parser(normalize_parameters) for parser in MANAGED_PARSERS]

    def parse(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
        lazy_read: bool = False,
    ) -> Optional[PromptInfo]:
        """
        Try to extract image generation parameters from the given image.

        Parameters:
            image (a PIL Image, filename, pathlib.Path object or a file object): The image to parse.
            lazy_read (bool): delay detailed metadata extraction until necessary.

        Warning: with lazy_read set to `True`, the returned image parameters may contain
        "garbage" information as some metadata checks will be delayed. Use when fast access to the
        original image parameters is needed. Manual verification of parameter data is advised.

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` function:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """

        def read_parameters(image: Image.Image):
            for parser in self.managed_parsers:
                prompt_info, _ = parser.read_parameters(image)
                if prompt_info:
                    return prompt_info
            return None

        if isinstance(image, Image.Image):
            prompt_info = read_parameters(image)
        else:
            with Image.open(image) as image_data:
                prompt_info = read_parameters(image_data)

        if prompt_info and not lazy_read:
            try:
                prompt_info.parse()  # pylint: disable=protected-access
            except ParserError:
                return None

        return prompt_info
