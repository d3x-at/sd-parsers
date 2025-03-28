from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .model import Model
from .prompt import Prompt


@dataclass(frozen=True)
class Sampler:
    """Represents a sampler used during image generation."""

    name: str
    """The name of the sampler"""

    parameters: Dict[str, Any]
    """Generation parameters, including `cfg_scale`, `seed`, `steps` and others."""

    sampler_id: Optional[str] = None
    """A unique id for this sampler (if present in the metadata)"""

    model: Optional[Model] = None
    """The checkpoint model used."""

    prompts: List[Prompt] = field(default_factory=list)
    """Positive prompts used by this sampler."""

    negative_prompts: List[Prompt] = field(default_factory=list)
    """Negative prompts used by this sampler."""

    def __hash__(self) -> int:
        return hash((self.sampler_id, self.name))
