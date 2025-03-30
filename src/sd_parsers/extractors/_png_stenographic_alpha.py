import gzip
import json
from contextlib import suppress
from typing import Any, Dict, Optional

from PIL.Image import Image

from sd_parsers.data.generators import Generators
from sd_parsers.exceptions import MetadataError

STEALTH_HEADER = "stealth_pngcomp"


class LSBExtractor:
    def __init__(self, img: Image):
        self.data = list(img.getdata())
        self.width, self.height = img.size
        self.data = [self.data[i * self.width : (i + 1) * self.width] for i in range(self.height)]
        self.dim = 4
        self.bits = 0
        self.byte = 0
        self.row = 0
        self.col = 0

    def _extract_next_bit(self):
        if self.row < self.height and self.col < self.width:
            bit = self.data[self.row][self.col][self.dim - 1] & 1
            self.bits += 1
            self.byte <<= 1
            self.byte |= bit
            self.row += 1
            if self.row == self.height:
                self.row = 0
                self.col += 1

    def get_one_byte(self):
        while self.bits < 8:
            self._extract_next_bit()
        byte = bytearray([self.byte])
        self.bits = 0
        self.byte = 0
        return byte

    def get_next_n_bytes(self, n):
        bytes_list = bytearray()
        for _ in range(n):
            byte = self.get_one_byte()
            if not byte:
                break
            bytes_list.extend(byte)
        return bytes_list

    def read_32bit_integer(self):
        bytes_list = self.get_next_n_bytes(4)
        if len(bytes_list) == 4:
            integer_value = int.from_bytes(bytes_list, byteorder="big")
            return integer_value
        else:
            return None

    @classmethod
    def extract_from(cls, image: Image):
        extractor = cls(image)

        read_magic = extractor.get_next_n_bytes(len(STEALTH_HEADER)).decode("utf-8")
        if STEALTH_HEADER != read_magic:
            raise ValueError(
                f'Header "{read_magic}" does not match the expected value of "{STEALTH_HEADER}"'
            )

        read_len = extractor.read_32bit_integer() // 8  # type: ignore
        raw_bytes = extractor.get_next_n_bytes(read_len)

        decompressed_bytes = gzip.decompress(raw_bytes).decode("utf-8")

        return decompressed_bytes


_image_id = None
_decompressed_bytes = None
_json_decoded = None


def png_stenographic_alpha(image: Image, generator: Generators) -> Optional[Dict[str, Any]]:
    """try to read stealth metadata from image"""
    global _image_id, _decompressed_bytes, _json_decoded

    if image.mode != "RGBA":
        raise MetadataError("image mode is not RGBA")

    image_id = id(image)

    # cache the last image data to prevent multiple extractions of the same instance
    if image_id != _image_id:
        _image_id = image_id
        _decompressed_bytes = None
        _json_decoded = None

        try:
            _decompressed_bytes = LSBExtractor.extract_from(image)

            with suppress(TypeError, json.JSONDecodeError):
                _json_decoded = json.loads(_decompressed_bytes)

        except Exception as error:
            raise MetadataError("error reading metadata") from error

    if generator == Generators.NOVELAI:
        return _json_decoded

    elif generator == Generators.AUTOMATIC1111:
        return {"parameters": _decompressed_bytes} if _decompressed_bytes else None

    return None
