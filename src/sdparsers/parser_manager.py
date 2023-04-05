from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from _typeshed import SupportsRead

from PIL import Image

from .parser import Parser
from .prompt_info import PromptInfo

DEFAULT_CONFIG = str(Path(__file__).resolve().parent / "config.json")


class ParserManager:
    '''keeps all available parsers ready for use'''
    parsers: List[Parser]

    def __init__(self, config_file: str = DEFAULT_CONFIG, process_items: bool = True):
        config = None
        if config_file:
            with open(config_file, "r", encoding="utf-8") as file:
                config = json.load(file)

        # initialize parsers
        self.parsers = [parser(config, process_items)
                        for parser in Parser.__subclasses__()]

    def parse(self, image: str | bytes | Path | SupportsRead[bytes] | Image.Image) -> Optional[PromptInfo]:
        if isinstance(image, Image.Image):
            return self._parse(image)
        else:
            with Image.open(image) as image_data:
                return self._parse(image_data)

    def _parse(self, image: Image.Image) -> Optional[PromptInfo]:
        '''try available parsers to get image information'''
        for parser in self.parsers:
            parameters = parser.parse(image)
            if parameters:
                return parameters
        return None
