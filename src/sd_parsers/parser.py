"""Provides the Parser base class & other useful utility."""
from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from PIL import ExifTags
from PIL.Image import Image

from . import data as _data

FormatField = Tuple[str, Tuple[List[str], str]]
RenameField = Tuple[str, str]

ReplacementRules = List[Union[RenameField, FormatField]]
"""Defines replacement rules as used in Parser.normalize_parameters().

Contains instruction to either rename a key (see `RenameField`),
or to create a new key using the given formatting instruction (see `FormatField`).
"""

ParseResult = Tuple[List[_data.Sampler], Dict[Any, Any]]
"""The result of Parser.parse() is a tuple of encountered samplers and remaining metadata."""

_EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}


class Parser(ABC):
    """Parser base class."""

    def __init__(self, normalize_parameters: bool = True):
        self.do_normalization_pass = normalize_parameters

    @property
    @abstractmethod
    def generator(self) -> _data.Generators:
        """Identifier for the inferred image generator."""

    @abstractmethod
    def read_parameters(
        self,
        image: Image,
        use_text: bool = True,
    ) -> Tuple[dict[str, Any], Any]:
        """
        Read generation parameters from image.

        returns image parameters (and a parsing_context if needed) if suitable image metadata has been found.
        """

    @abstractmethod
    def parse(self, parameters: Dict[str, Any], parsing_context: Any) -> ParseResult:
        """Extract image generation information from the image metadata."""

    def normalize_parameters(
        self,
        parameters: Union[Dict[str, Any], Iterable[Tuple[str, Any]]],
        replacement_rules: Optional[ReplacementRules] = None,
        to_lowercase=True,
        replace_whitespace=True,
    ) -> Dict[str, Any]:
        """
        Apply replacement rules and basic formatting to the keys of select image metadata entries.

        Returns a dictionary with normalized parameter values.

        Override to alter the applied standardization logic.
        """
        if self.do_normalization_pass:
            return _normalize_parameters(
                parameters, replacement_rules, to_lowercase, replace_whitespace
            )

        return parameters if isinstance(parameters, dict) else dict(parameters)  # type: ignore


def _normalize_parameters(
    parameters: Union[Dict[str, Any], Iterable[Tuple[str, Any]]],
    replacement_rules: Optional[ReplacementRules] = None,
    to_lowercase=True,
    replace_whitespace=True,
) -> Dict[str, Any]:
    """
    Apply replacement rules and basic formatting to the keys of select image metadata entries.

    Returns a dictionary with normalized parameter values.
    """

    raw_props = dict(parameters)
    processed = {}

    if replacement_rules:
        for property_key, instruction in replacement_rules:
            # rename field instruction
            if isinstance(instruction, str):
                with suppress(KeyError):
                    processed[instruction] = raw_props.pop(property_key)

            # format field instruction
            else:
                format_values, format_string = instruction
                with suppress(KeyError):
                    processed[property_key] = format_string.format(
                        **{key: raw_props[key] for key in format_values}
                    )

    for key, value in raw_props.items():
        if to_lowercase:
            key = key.lower()

        if replace_whitespace:
            key = key.replace(" ", "_")

        processed[key] = value

    return processed


def get_exif_value(
    image: Image,
    key: str,
    *,
    ifd_tag: int = 0x8769,
    prefix_length: int = 8,
    encoding: str = "utf_16_be",
) -> str:
    """Read the value for a given key out of the images exif data."""
    exif_value = image.getexif().get_ifd(ifd_tag)[_EXIF_TAGS[key]]
    if len(exif_value) <= prefix_length:
        raise ValueError("exif value too short")
    return exif_value[prefix_length:].decode(encoding)


def pop_keys(keys: Iterable[str], dictionary: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    """
    Remove dictionary entries specified by `keys` from the given dictionary.

    Ignores non-existing keys.

    Returns an iterator over the actually removed keys and their corresponding values.
    """
    for key in keys:
        with suppress(KeyError):
            yield key, dictionary.pop(key)
