from typing import Any, Dict
from PIL import Image
from sd_parsers.data import Generators


def png_image_info(image: Image.Image, _: Generators) -> Dict[str, Any]:
    """use image.info"""
    return image.info
