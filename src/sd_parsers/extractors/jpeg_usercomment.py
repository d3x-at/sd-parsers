from contextlib import suppress
from PIL import Image
from typing import Any, Dict

from sd_parsers.data import Generators
from ._get_exif_value import get_exif_value

_image_id = None
_usercomment = None


def usercomment(image: Image.Image, generator: Generators) -> Dict[str, Any] | None:
    """use image.info"""
    global _image_id, _usercomment

    # cache the last image data to prevent multiple extractions of the same instance
    image_id = id(image)
    if image_id != _image_id:
        _image_id = image_id

        with suppress(KeyError, ValueError):
            _usercomment = get_exif_value(image, "UserComment")

    if _usercomment is None:
        return None

    if generator in (Generators.AUTOMATIC1111, Generators.FOOOCUS):
        return {"parameters": _usercomment}

    return None
