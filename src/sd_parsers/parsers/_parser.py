"""Provides the Parser base class & other useful utility."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from sd_parsers.data import Generators, PromptInfo

FormatField = Tuple[str, Tuple[List[str], str]]
RenameField = Tuple[str, str]

ReplacementRules = List[Union[RenameField, FormatField]]
"""Defines replacement rules as used in Parser.normalize_parameters().

Contains instruction to either rename a key (see `RenameField`),
or to create a new key using the given formatting instruction (see `FormatField`).
"""


class Parser(ABC):
    """Parser base class."""

    generator = Generators.UNKNOWN

    def __init__(self, normalize_parameters: bool = True, debug: bool = False):
        self.do_normalization_pass = normalize_parameters
        self._debug = debug

    @abstractmethod
    def parse(self, parameters: Dict[str, Any]) -> PromptInfo:
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

        """
        if not self.do_normalization_pass:
            return parameters if isinstance(parameters, dict) else dict(parameters)  # type: ignore

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


def pop_keys(keys: Iterable[str], dictionary: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    """
    Remove dictionary entries specified by `keys` from the given dictionary.

    Ignores non-existing keys.

    Returns an iterator over the actually removed keys and their corresponding values.
    """
    for key in keys:
        with suppress(KeyError):
            yield key, dictionary.pop(key)
