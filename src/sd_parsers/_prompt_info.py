"""Provides the PromptInfo class."""
from __future__ import annotations

import itertools
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Set

from ._exceptions import ParserError

if TYPE_CHECKING:
    from ._models import Model, Prompt, Sampler
    from ._parser import Generators, Parser

logger = logging.getLogger(__name__)


class PromptInfo:
    """Contains structured image generation parameters."""

    parameters: Dict[str, Any]
    """The original parameters as found in the image metadata."""

    def __init__(self, parser: Parser, parameters: Dict[str, Any]):
        """
        Initializes a PromptInfo Object

        Parameters:
            Parser (sd_parsers.Parser): The parser object used to obtain the given image parameters.
            parameters (Dict[str, Any]): A dictionary containing the image metadata.
        """
        self._parser = parser
        self.parameters = parameters

    def parse(self):
        """Populate sampler information and metadata."""
        self._samplers, self._metadata = self._parser.parse(self.parameters)
        return self._samplers, self._metadata

    @property
    def generator(self) -> Generators:
        """Image generater which might have produced the parsed image."""
        return self._parser.generator

    _samplers = None

    @property
    def samplers(self) -> List[Sampler]:
        """Samplers used in generating the parsed image."""
        if self._samplers is None:
            try:
                self._samplers, self._metadata = self.parse()
            except ParserError:
                self._samplers, self._metadata = [], {}
        return self._samplers

    _metadata = None

    @property
    def metadata(self) -> dict:
        """
        Additional parameters which are found in the image metadata.

        Highly dependent on the respective image generator.
        """
        if self._metadata is None:
            try:
                self._samplers, self._metadata = self.parse()
            except ParserError:
                self._samplers, self._metadata = [], {}
        return self._metadata

    _prompts = None

    @property
    def prompts(self) -> Set[Prompt]:
        """Prompts used in generating the parsed image."""
        if self._prompts is None:
            self._prompts = set(
                itertools.chain.from_iterable(sampler.prompts for sampler in self.samplers)
            )
        return self._prompts

    _negative_prompts = None

    @property
    def negative_prompts(self) -> Set[Prompt]:
        """Negative prompts used in generating the parsed image."""
        if self._negative_prompts is None:
            self._negative_prompts = set(
                itertools.chain.from_iterable(sampler.negative_prompts for sampler in self.samplers)
            )
        return self._negative_prompts

    _models = None

    @property
    def models(self) -> Set[Model]:
        """Models used in generating the parsed image."""
        if self._models is None:
            self._models = set(sampler.model for sampler in self.samplers if sampler.model)
        return self._models
