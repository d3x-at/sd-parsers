from . import png_image_info, png_image_text, jpeg_usercomment

import typing as _typing
from sd_parsers.data.generators import Generators as _Generators
from PIL.Image import Image as _Image

_ExtractorType = _typing.Callable[
    [_Image, _Generators], _typing.Optional[_typing.Dict[str, _typing.Any]]
]

METADATA_EXTRACTORS: _typing.Dict[str, _typing.List[_typing.List[_ExtractorType]]] = {
    "PNG": [
        [png_image_info.png_image_info],
        [png_image_text.png_image_text],
    ],
    "JPEG": [
        [jpeg_usercomment.usercomment],
    ],
    "WEBP": [
        [jpeg_usercomment.usercomment],
    ],
}
"""
A list of retrieval functions to provide multiple metadata entrypoints for each parser module.

Entries are sorted by parsing eagerness:
"PNG": [
        [FAST, ...],
        [DEFAULT, ...],
        [EAGER, ...],
    ]
"""
