import typing as _typing
from enum import Enum as _Enum

from PIL.Image import Image as _Image

from sd_parsers.data.generators import Generators as _Generators

from ._jpeg_usercomment import jpeg_usercomment
from ._png_image_info import png_image_info
from ._png_image_text import png_image_text
from ._png_stenographic_alpha import png_stenographic_alpha

_ExtractorType = _typing.Callable[
    [_Image, _Generators], _typing.Optional[_typing.Dict[str, _typing.Any]]
]


class Eagerness(_Enum):
    FAST = 1
    DEFAULT = 2
    EAGER = 3


METADATA_EXTRACTORS: _typing.Dict[str, _typing.Dict[Eagerness, _typing.List[_ExtractorType]]] = {
    "PNG": {
        Eagerness.FAST: [png_image_info],
        Eagerness.DEFAULT: [png_image_text],
        Eagerness.EAGER: [png_stenographic_alpha],
    },
    "JPEG": {
        Eagerness.FAST: [jpeg_usercomment],
    },
    "WEBP": {
        Eagerness.FAST: [jpeg_usercomment],
    },
}
"""
A list of retrieval functions to provide multiple metadata entrypoints for each parser module.
"""
