"""Provides the PromptInfo class."""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterable

from .exceptions import ParserError

if TYPE_CHECKING:
    from ._models import Model, Prompt, Sampler
    from ._parser import Generators, Parser


@dataclass
class PromptInfo:
    """Contains structured image generation parameters."""

    _parser: Parser
    """parser (sdparsers.Parser): The parser object used to obtain the given image parameters."""

    parameters: Dict[str, Any]
    """The original parameters as found in the image metadata."""

    _parsing_context: Any = None
    """
        Any information needed during the parsing pass.
        Passed on to the parser's parse() method.
    """

    def parse(self):
        """Populate sampler information and metadata."""
        self._samplers, self._metadata = self._parser.parse(self.parameters, self._parsing_context)
        return self._samplers, self._metadata

    @property
    def generator(self) -> Generators:
        """Image generater which might have produced the parsed image."""
        return self._parser.generator

    _samplers = None

    @property
    def samplers(self) -> Iterable[Sampler]:
        """Samplers used in generating the parsed image."""
        if self._samplers is None:
            try:
                self.parse()
            except ParserError:
                self._samplers, self._metadata = [], {}
        return self._samplers  # type: ignore

    _metadata = None

    @property
    def metadata(self) -> dict[Any, Any]:
        """
        Additional parameters which are found in the image metadata.

        Highly dependent on the respective image generator.
        """
        if self._metadata is None:
            try:
                self.parse()
            except ParserError:
                self._samplers, self._metadata = [], {}
        return self._metadata  # type: ignore

    _prompts = None

    @property
    def prompts(self) -> Iterable[Prompt]:
        """Prompts used in generating the parsed image."""
        if self._prompts is None:
            self._prompts = set(
                itertools.chain.from_iterable(sampler.prompts for sampler in self.samplers)
            )
        return self._prompts

    _negative_prompts = None

    @property
    def negative_prompts(self) -> Iterable[Prompt]:
        """Negative prompts used in generating the parsed image."""
        if self._negative_prompts is None:
            self._negative_prompts = set(
                itertools.chain.from_iterable(sampler.negative_prompts for sampler in self.samplers)
            )
        return self._negative_prompts

    _models = None

    @property
    def models(self) -> Iterable[Model]:
        """Models used in generating the parsed image."""
        if self._models is None:
            self._models = set(sampler.model for sampler in self.samplers if sampler.model)
        return self._models

    def __str__(self):
        return (
            f"PromptInfo(generator={self.generator}, "
            f"prompts={self.prompts}, "
            f"negative_prompts={self.negative_prompts}, "
            f"samplers={self.samplers}, "
            f"models={self.models}, "
            f"metadata={self.metadata}, "
            "parameters={...})"
        )
