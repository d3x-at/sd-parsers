"""Data classes representing a subset of image generation parameters."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional

from .exceptions import ParserError

if TYPE_CHECKING:
    from .parser import Parser


class Generators(str, Enum):
    """Image generator identifiers."""

    UNKNOWN = "Unknown"
    AUTOMATIC1111 = "AUTOMATIC1111"
    COMFYUI = "ComfyUI"
    INVOKEAI = "InvokeAI"
    NOVELAI = "NovelAI"
    FOOOCUS = "Fooocus"


@dataclass(frozen=True)
class Prompt:
    """Represents an image generation prompt."""

    value: str
    """The value of the prompt."""

    prompt_id: Optional[int] = None
    """Prompt id"""

    metadata: Dict[Any, Any] = field(default_factory=dict)
    """
    Additional generator-specific information.
    
    Highly dependent on the respective image generator.
    """

    def __str__(self):
        return self.value

    def __hash__(self) -> int:
        return hash((self.prompt_id, self.value))


@dataclass(frozen=True)
class Model:
    """Represents a checkpoint model used during image generation."""

    name: Optional[str] = None
    hash: Optional[str] = None
    model_id: Optional[int] = None

    metadata: Dict[Any, Any] = field(default_factory=dict)
    """
    Additional generator-specific information.
    
    Highly dependent on the respective image generator.
    """

    def __hash__(self) -> int:
        return hash((self.model_id, self.name))


@dataclass(frozen=True)
class Sampler:
    """Represents a model used during image generation."""

    name: str
    parameters: Dict[str, Any]
    sampler_id: Optional[int] = None
    model: Optional[Model] = None
    prompts: List[Prompt] = field(default_factory=list)
    negative_prompts: List[Prompt] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash((self.sampler_id, self.name))


class PromptInfo:
    """Contains structured image generation parameters."""

    def __init__(self, parser: Parser, parameters: dict[str, Any], parsing_context: Any = None):
        """
        Initializes a ParserManager object.

        Parameters:
            parser: The parser object used to obtain the given image parameters.
            parameters: The original generation parameters as found in the image metadata.
            parsing_context: Any information needed during the parsing pass. Passed on to the parser's parse() method.
        """
        self._parser = parser
        self._parameters = parameters
        self._parsing_context = parsing_context

    def _parse(self):
        """Populate sampler information and metadata."""
        self._samplers, self._metadata = self._parser.parse(self._parameters, self._parsing_context)
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
                self._parse()
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
                self._parse()
            except ParserError:
                self._samplers, self._metadata = [], {}
        return self._metadata  # type: ignore

    @property
    def full_prompt(self) -> str:
        """
        Full prompt if present in the image metadata.
        Otherwise, a simple concatenation of all prompts found in the generation data.

        Reproducibility of the source image using this data is not guaranteed (=rather unlikely).
        """
        try:
            return self.metadata["full_prompt"]
        except KeyError:
            return ", ".join(map(str, self.prompts))

    @property
    def full_negative_prompt(self) -> str:
        """
        Full negative prompt if present in the image metadata.
        Otherwise, a simple concatenation of all negative prompts found in the generation data.

        Reproducibility of the source image using this data is not guaranteed (=rather unlikely).
        """
        try:
            return self.metadata["full_negative_prompt"]
        except KeyError:
            return ", ".join(map(str, self.negative_prompts))

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
            f'full_prompt="{self.full_prompt}", '
            f'full_negative_prompt="{self.full_negative_prompt}", '
            f"prompts={self.prompts}, "
            f"negative_prompts={self.negative_prompts}, "
            f"samplers={self.samplers}, "
            f"models={self.models}, "
            f"metadata={self.metadata}"
        )
