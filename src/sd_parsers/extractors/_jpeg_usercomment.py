from PIL import Image
from typing import Any, Dict, Optional

from sd_parsers.data import Generators
from sd_parsers.exceptions import MetadataError
from ._get_exif_value import get_exif_value

_image_id = None
_usercomment = None


def jpeg_usercomment(image: Image.Image, generator: Generators) -> Optional[Dict[str, Any]]:
    """use image.info"""
    global _image_id, _usercomment

    # cache the last image data to prevent multiple extractions of the same instance
    image_id = id(image)
    if image_id != _image_id:
        _image_id = image_id
        _usercomment = None

        try:
            _usercomment = get_exif_value(image, "UserComment")
        except (KeyError, ValueError) as error:
            raise MetadataError("error reading UserComment") from error

    if _usercomment is None:
        return None

    if generator in (Generators.AUTOMATIC1111, Generators.FOOOCUS):
        return {"parameters": _usercomment}

    return None
