"""Data classes representing a subset of image generation parameters."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Prompt:
    """Represents an image generation prompt."""

    value: str
    """The value of the prompt."""

    prompt_id: Optional[int] = None
    """Prompt id"""

    parameters: Dict[str, Any] = field(default_factory=dict)
    """Additional prompt parameters"""

    def __hash__(self) -> int:
        return hash((self.prompt_id, self.value))


@dataclass(frozen=True)
class Model:
    """Represents a model used during image generation."""

    model_id: Optional[int] = None
    name: Optional[str] = None
    model_hash: Optional[str] = None

    parameters: Dict[str, Any] = field(default_factory=dict)
    """Additional model parameters"""

    def __hash__(self) -> int:
        return hash((self.model_id, self.name))


@dataclass
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
