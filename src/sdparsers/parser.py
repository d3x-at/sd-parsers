'''logic for getting prompts data out of different image formats'''
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Union

import PIL.ExifTags
from PIL import Image

from . import PromptInfo

# pylint: disable=too-few-public-methods

_EXIF_TAGS = {v: k for k, v in PIL.ExifTags.TAGS.items()}


def get_exif_value(image, key, prefix_length: int = 8, encoding: str = 'utf_16_be'):
    try:
        exif_value = image.getexif().get_ifd(0x8769)[_EXIF_TAGS[key]]
        if len(exif_value) > prefix_length:
            return exif_value[prefix_length:].decode(encoding, errors='replace')
    except KeyError:
        pass
    return None


class Parser(ABC):
    '''parser base class'''
    PRIORITY = 0

    def __init__(self, config: Optional[dict] = None, process_items: bool = True):
        self.config = {} if config is None else config
        self._process_items = process_items

    @abstractmethod
    def parse(self, image: Image.Image) -> Optional[PromptInfo]:
        '''parse'''

    def _process_metadata(self, extracted_fields: Union[dict, Iterable[Tuple]]) -> dict:
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
                    # require all values to be present
                    format_values = {}
                    try:
                        for x in recipe['values']:
                            format_values[x] = fields.pop(x)
                        value = recipe['format'].format(**format_values)
                        yield (key, value)
                    except KeyError:
                        # put back popped keys if the replacement failed
                        fields.update(format_values)

        # remaining (unchanged) items
        for key, value in fields.items():
            yield (key.lower().replace(" ", "_"), value)
