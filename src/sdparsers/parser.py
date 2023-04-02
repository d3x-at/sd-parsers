'''logic for getting prompts data out of different image formats'''
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Iterable
from PIL import Image

from . import PromptInfo

# pylint: disable=too-few-public-methods


class Parser(ABC):
    '''parser base class'''

    def __init__(self, config: Optional[dict] = None, process_items: bool = True):
        self._config = config
        self._process_items = process_items

    @abstractmethod
    def parse(self, image: Image.Image) -> Optional[PromptInfo]:
        '''parse'''

    @property
    def custom_fields(self) -> dict:
        '''field value translation dictionary'''
        if self._config is None:
            return {}
        try:
            return self._config["parsers"][type(self).__name__]["fields"]
        except KeyError:
            return {}

    def process_items(self, extracted_fields: Iterable[Tuple[str, str]]):
        if not self._process_items:
            return list(extracted_fields)

        return list(self.update_item_values(extracted_fields))

    def update_item_values(self, extracted_fields: Iterable[Tuple[str, str]]):
        fields = dict(extracted_fields)
        for key, recipe in self.custom_fields.items():
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
