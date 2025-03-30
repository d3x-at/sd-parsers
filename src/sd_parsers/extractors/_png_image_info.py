from typing import Any, Dict
from PIL import Image


def png_image_info(image: Image.Image, _) -> Dict[str, Any]:
    """use image.info"""
    return image.info
