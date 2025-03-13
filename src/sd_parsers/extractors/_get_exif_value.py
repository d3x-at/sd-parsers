from PIL import ExifTags as _ExifTags
from PIL import Image as _Image

_EXIF_TAGS = {v: k for k, v in _ExifTags.TAGS.items()}


def get_exif_value(
    image: _Image.Image,
    key: str,
    *,
    ifd_tag: int = 0x8769,
    prefix_length: int = 8,
    encoding: str = "utf_16_be",
) -> str:
    """Read the value for a given key out of the images exif data."""
    exif_value = image.getexif().get_ifd(ifd_tag)[_EXIF_TAGS[key]]
    if len(exif_value) <= prefix_length:
        raise ValueError("exif value too short")
    return exif_value[prefix_length:].decode(encoding)
