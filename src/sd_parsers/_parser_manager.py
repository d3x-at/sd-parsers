"""Provides the ParserManager class."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from PIL import Image

from ._parser import Parser
from ._prompt_info import PromptInfo
from .exceptions import ParserError
from .parsers import MANAGED_PARSERS

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
        *,
        normalize_parameters: bool = True,
        two_pass: bool = True,
        lazy_read: bool = False,
        managed_parsers: Optional[List[Parser]] = None,
    ):
        """
        Initializes a ParserManager object.

        Optional Parameters:
            normalize_parameters (bool): Try to unify the parameter keys of the parser outputs.
            managed_parsers (list[Parser]): A list of parsers to be managed.
            two_pass (bool): for PNG images, use `Image.info` before using `Image.text` as metadata source.
            lazy_read (bool): delay detailed metadata extraction until necessary.


        The performance effects of two-pass parsing depends on the given image files.
        If the image files are correctly formed and can be read with one of the supported parser modules,
        setting `two_pass` to `True` will considerably shorten the time needed to read the image parameters.

        Warning: with lazy_read set to `True`, the returned image parameters may contain
        "garbage" information as some metadata checks will be delayed. Use when fast access to the
        original image parameters is needed. Manual verification of parameter data is advised.
        """
        self.two_pass = two_pass
        self.lazy_read = lazy_read

        if managed_parsers is not None:
            self.managed_parsers = managed_parsers
        else:
            self.managed_parsers = [parser(normalize_parameters) for parser in MANAGED_PARSERS]

    def parse(
        self,
        image: Union[str, bytes, Path, SupportsRead[bytes], Image.Image],
    ) -> Optional[PromptInfo]:
        """
        Try to extract image generation parameters from the given image.

        Parameters:
            image (a PIL Image, filename, pathlib.Path object or a file object): The image to parse.

        If not called with a PIL.Image for `image`, the following exceptions can be thrown by the
        underlying `Image.open()` function:
        - FileNotFoundError: If the file cannot be found.
        - PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        - ValueError: If a StringIO instance is used for `image`.
        """

        def read_parameters(image: Image.Image):
            prompt_info = None
            # two_pass only makes sense with PNG images
            two_pass = image.format == "PNG" if self.two_pass else False

            for use_text in [False, True] if two_pass else [True]:
                for parser in self.managed_parsers:
                    try:
                        prompt_info = parser.read_parameters(image, use_text)
                        if prompt_info is None:
                            continue

                        if not self.lazy_read:
                            prompt_info.parse()

                    except ParserError:
                        continue

                    return prompt_info
            return None

        if isinstance(image, Image.Image):
            prompt_info = read_parameters(image)
        else:
            with Image.open(image) as _image:
                prompt_info = read_parameters(_image)

        return prompt_info
