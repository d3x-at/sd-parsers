'''logic for getting prompts data out of different image formats'''
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Union

from PIL import Image

from . import PromptInfo

# pylint: disable=too-few-public-methods


class Parser(ABC):
    '''parser base class'''
    PRIORITY = 0

    def __init__(self, config: Optional[dict] = None, process_items: bool = True):
        self.config = {} if config is None else config
        self._process_items = process_items

    @abstractmethod
    def parse(self, image: Image.Image) -> Optional[PromptInfo]:
        '''parse'''

    def _process_metadata(self, extracted_fields: Union[dict, Iterable[Tuple]]):
        if self._process_items:
            return dict(self._update_item_values(extracted_fields))
        return dict(extracted_fields)

    def _update_item_values(self, extracted_fields: Union[dict, Iterable[Tuple]]):
        fields = dict(extracted_fields)
        if "fields" in self.config:
            for key, recipe in self.config["fields"].items():
                if isinstance(recipe, str):
                    value = fields.pop(key, None)
                    if value is not None:
                        yield (recipe, value)

                elif isinstance(recipe, dict):
                    format_values = (fields.pop(x, None) for x in recipe['values'])
                    value = recipe['format'].format(*format_values)
                    yield (key, value)

        # remaining (unchanged) items
        for key, value in fields.items():
            yield (key.lower().replace(" ", "_"), value)
