"""Data classes representing a subset of image generation parameters."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional

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

    prompt_id: int
    """Prompt id"""

    value: str
    """The value of the prompt."""

    metadata: Dict[Any, Any] = field(default_factory=dict)
    """
    Additional generator-specific information.
    
    Highly dependent on the respective image generator.
    """

    def __str__(self):
        return self.value

    def __hash__(self) -> int:
        return hash(self.prompt_id)


@dataclass(frozen=True)
class Model:
    """Represents a checkpoint model used during image generation."""

    name: Optional[str] = None
    """Name of the checkpoint model (if found)."""

    hash: Optional[str] = None
    """Hash value of the checkpoint model. (if found)"""

    model_id: Optional[int] = None
    """Model id"""

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
    """The name of the sampler"""

    parameters: Dict[str, Any]
    """Generation parameters, including `cfg_scale`, `seed`, `steps` and others."""

    sampler_id: Optional[int] = None
    """A unique id for this sampler (if present in the metadata)"""

    model: Optional[Model] = None
    """The checkpoint model used."""

    prompts: List[Prompt] = field(default_factory=list)
    """Positive prompts used by this sampler."""

    negative_prompts: List[Prompt] = field(default_factory=list)
    """Negative prompts used by this sampler."""

    def __hash__(self) -> int:
        return hash((self.sampler_id, self.name))


class PromptInfo:
    """Contains structured image generation parameters."""

    samplers: List[Sampler]
    """Samplers used in generating the parsed image."""

    metadata: Dict[Any, Any]
    """
        Additional parameters which are found in the image metadata.

        Highly dependent on the respective image generator.
    """

    def __init__(
        self,
        parser: Parser,
        samplers: List[Sampler],
        metadata: Dict[Any, Any],
    ):
        """
        Initializes a ParserManager object.

        Parameters:
            parser: The parser object used to obtain the given image parameters.
            samplers: The samplers used in generating the parsed image.
            metadata: Any additional parameters which are found in the image metadata.
        """
        self._parser = parser
        self.samplers = samplers
        self.metadata = metadata

    @property
    def generator(self) -> Generators:
        """Image generater which might have produced the parsed image."""
        return self._parser.generator

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
    def prompts(self) -> List[Prompt]:
        """Prompts used in generating the parsed image."""
        if self._prompts is None:
            unique_prompts = set()
            self._prompts = []

            for prompt in itertools.chain.from_iterable(
                sampler.prompts for sampler in self.samplers
            ):
                if prompt in unique_prompts:
                    continue

                unique_prompts.add(prompt)
                self._prompts.append(prompt)

        return self._prompts

    _negative_prompts = None

    @property
    def negative_prompts(self) -> List[Prompt]:
        """Negative prompts used in generating the parsed image."""
        if self._negative_prompts is None:
            unique_prompts = set()
            self._negative_prompts = []

            for prompt in itertools.chain.from_iterable(
                sampler.negative_prompts for sampler in self.samplers
            ):
                if prompt in unique_prompts:
                    continue

                unique_prompts.add(prompt)
                self._negative_prompts.append(prompt)

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
