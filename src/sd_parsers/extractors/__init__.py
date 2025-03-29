import typing as _typing
from enum import Enum as _Enum

from PIL.Image import Image as _Image

from sd_parsers.data.generators import Generators as _Generators
from . import png_image_info, png_image_text, jpeg_usercomment, png_stenographic_alpha

_ExtractorType = _typing.Callable[
    [_Image, _Generators], _typing.Optional[_typing.Dict[str, _typing.Any]]
]


class Eagerness(_Enum):
    FAST = 1
    DEFAULT = 2
    EAGER = 3


METADATA_EXTRACTORS: _typing.Dict[str, _typing.Dict[Eagerness, _typing.List[_ExtractorType]]] = {
    "PNG": {
        Eagerness.FAST: [png_image_info.png_image_info],
        Eagerness.DEFAULT: [png_image_text.png_image_text],
        Eagerness.EAGER: [png_stenographic_alpha.stenographic_alpha],
    },
    "JPEG": {
        Eagerness.FAST: [jpeg_usercomment.usercomment],
    },
    "WEBP": {
        Eagerness.FAST: [jpeg_usercomment.usercomment],
    },
}
"""
A list of retrieval functions to provide multiple metadata entrypoints for each parser module.
"""
