"""Data classes representing a subset of image generation parameters."""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List

from .generators import Generators
from .model import Model
from .prompt import Prompt
from .sampler import Sampler


@dataclass
class PromptInfo:
    """Contains structured image generation parameters."""

    generator: Generators
    """Image generator which might have produced the parsed image."""

    samplers: List[Sampler]
    """Samplers used in generating the parsed image."""

    metadata: Dict[Any, Any]
    """
        Additional parameters which are found in the image metadata.

        Highly dependent on the respective image generator.
    """

    raw_parameters: Dict[str, Any]
    """
        Unprocessed parameters as found in the parsed image.
    """

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

    def asdict(self):
        return {
            "full_prompt": self.full_prompt,
            "full_negative_prompt": self.full_negative_prompt,
            **asdict(self),
        }

    def to_json(self):
        return json.dumps(self.asdict())
