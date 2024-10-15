from dataclasses import dataclass, field
from typing import Any, Dict


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
