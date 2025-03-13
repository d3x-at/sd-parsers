from contextlib import suppress
from typing import Any, Dict
from PIL import Image
from sd_parsers.data import Generators


def png_image_text(image: Image.Image, _: Generators) -> Dict[str, Any] | None:
    """use image.text property (iTxt, tEXt and zTXt chunks may appear at the end of the file)"""
    with suppress(AttributeError):
        return image.text  # type: ignore
    return None
