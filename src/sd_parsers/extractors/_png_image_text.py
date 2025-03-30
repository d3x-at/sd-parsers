from typing import Any, Dict, Optional
from PIL import Image

from sd_parsers.exceptions import MetadataError


def png_image_text(image: Image.Image, _) -> Optional[Dict[str, Any]]:
    """use PngImagePlugin.text property (iTxt, tEXt and zTXt chunks may appear at the end of the file)"""
    try:
        return image.text  # type: ignore
    except AttributeError as error:
        raise MetadataError("error reading Image.text property") from error
