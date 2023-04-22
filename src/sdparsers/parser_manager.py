import json
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type, Union

if TYPE_CHECKING:
    from _typeshed import SupportsRead

from PIL import Image

from .parser import Parser
from .prompt_info import PromptInfo

DEFAULT_CONFIG = str(Path(__file__).resolve().parent / "config.json")


def _get_parsers(parser: Type[Parser] = Parser):
    for child in parser.__subclasses__():
        yield child
        yield from _get_parsers(child)


class ParserManager:
    '''keeps all available parsers ready for use'''
    parsers: List[Parser]

    def __init__(self, config_file: str = DEFAULT_CONFIG, process_items: bool = True):
        config = None
        if config_file:
            with open(config_file, "r", encoding="utf-8") as file:
                config = json.load(file)

        def get_config(parser: Type[Parser]) -> Optional[dict]:
            if config and "parsers" in config:
                return config["parsers"].get(parser.__name__)
            return None

        # initialize parsers
        self.parsers = sorted((parser(get_config(parser), process_items)
                               for parser in _get_parsers()),
                              key=lambda p: p.PRIORITY, reverse=True)

    def parse(self, image: Union[str, bytes, Path,
                                 'SupportsRead[bytes]',
                                 Image.Image]) -> Optional[PromptInfo]:
        '''try available parsers to get image information

        The following exceptions can be thrown by the underlying `Image.open()`
        function:
        :exception FileNotFoundError: If the file cannot be found.
        :exception PIL.UnidentifiedImageError: If the image cannot be opened
        and identified.
        :exception ValueError: If a StringIO instance is used for fp.
        '''
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
