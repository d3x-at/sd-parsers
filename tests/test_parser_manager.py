import io
import logging

import PIL
import pytest
from sd_parsers import ParserManager

from tests.tools import RESOURCE_PATH

logger = logging.getLogger(__name__)


def test_parse_images():
    parser_manager = ParserManager()
    for filename in (RESOURCE_PATH / "parsers").rglob("*.*"):
        if filename.suffix.lower() not in (".jpg", ".png", ".webp"):
            continue
        folder_name = filename.parent.name

        logger.info("parsing %s", filename)
        prompt_info = parser_manager.parse(filename)
        assert prompt_info is not None
        assert prompt_info.generator == folder_name
        assert prompt_info.prompts


def test_parse_missing_file():
    parser_manager = ParserManager()
    with pytest.raises(FileNotFoundError):
        parser_manager.parse(RESOURCE_PATH / "bad_images" / "missing_file.png")


def test_parse_empty_file():
    parser_manager = ParserManager()
    with pytest.raises(PIL.UnidentifiedImageError):
        parser_manager.parse(RESOURCE_PATH / "bad_images" / "empty_file.png")


def test_parse_text_string():
    parser_manager = ParserManager()
    with pytest.raises(ValueError):
        with io.StringIO("this is not an image") as file:
            parser_manager.parse(file)  # type: ignore


def test_parse_text_after_idat():
    parser_manager = ParserManager()
    prompt_info = parser_manager.parse(RESOURCE_PATH / "bad_images" / "text_after_idat.png")
    assert prompt_info is not None
    assert prompt_info.prompts
