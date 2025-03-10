from .png_image_info import png_image_info
from .png_image_text import png_image_text

METADATA_EXTRACTORS = {
    "PNG": [
        png_image_info,
        png_image_text,
    ]
}
"""A list of retrieval functions to provide multiple metadata entrypoints for each parser module."""


__all__ = ["png_image_info", "png_image_text"]
