from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Prompt:
    """Represents an image generation prompt."""

    value: str
    """The value of the prompt."""

    prompt_id: Optional[str] = None
    """Prompt id"""

    metadata: Dict[Any, Any] = field(default_factory=dict)
    """
    Additional generator-specific information.
    
    Highly dependent on the respective image generator.
    """

    def __str__(self):
        return self.value

    def __hash__(self) -> int:
        return hash((self.value, self.prompt_id))
