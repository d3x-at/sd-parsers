from . import png_image_info, png_image_text, jpeg_usercomment


METADATA_EXTRACTORS = {
    "PNG": [
        png_image_info.png_image_info,
        png_image_text.png_image_text,
    ],
    "JPEG": [
        jpeg_usercomment.usercomment,
    ],
    "WEBP": [
        jpeg_usercomment.usercomment,
    ],
}
"""A list of retrieval functions to provide multiple metadata entrypoints for each parser module."""
