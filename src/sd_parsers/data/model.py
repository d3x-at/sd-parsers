from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Model:
    """Represents a checkpoint model used during image generation."""

    name: Optional[str] = None
    """Name of the checkpoint model (if found)."""

    hash: Optional[str] = None
    """Hash value of the checkpoint model. (if found)"""

    model_id: Optional[str] = None
    """Model id"""

    metadata: Dict[Any, Any] = field(default_factory=dict)
    """
    Additional generator-specific information.
    
    Highly dependent on the respective image generator.
    """

    def __post_init__(self):
        if self.name is None and self.hash is None:
            raise ValueError("Either name or hash need to be given.")

    def __str__(self) -> str:
        if self.name is None:
            return self.hash or ""
        return self.name

    def __hash__(self) -> int:
        return hash((self.model_id, self.name, self.hash))
