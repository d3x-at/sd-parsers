import io
import unittest

import PIL

from sdparsers import ParserManager, PromptInfo
from sdparsers.parsers import (AUTOMATIC1111Parser, ComfyUIParser,
                               InvokeAIParser, NovelAIParser)

from tools import RESOURCE_PATH

PARSER_FOLDERS = {
    'automatic1111': AUTOMATIC1111Parser.GENERATOR_ID,
    'comfyui': ComfyUIParser.GENERATOR_ID,
    'invokeai': InvokeAIParser.GENERATOR_ID,
    'novelai': NovelAIParser.GENERATOR_ID
}


def get_image_files():
    for child in RESOURCE_PATH.rglob('*.*'):
        if child.suffix.lower() in (".jpg", ".png", ".webp"):
            folder = child.parent.name
            if folder in PARSER_FOLDERS:
                yield child, PARSER_FOLDERS[folder]


class ParserManagerTester(unittest.TestCase):

    def test_initialize(self):
        parser_manager = ParserManager()
        self.assertIsNotNone(parser_manager)
        self.assertTrue(len(parser_manager.parsers) >= 4)

    def test_load_custom_comfig(self):
        CUSTOM_CONFIG = str(RESOURCE_PATH / "parser_manager" / "test_config.json")
        parser_manager = ParserManager(config_file=CUSTOM_CONFIG)
        parser = (parser for parser in parser_manager.parsers
                  if isinstance(parser, ComfyUIParser)).__next__()
        self.assertEqual(parser.config["test_config"], "test_value")

    def test_parse_images(self):
        parser_manager = ParserManager()
        for image, expected_generator in get_image_files():
            with self.subTest(image="/".join(image.parts[-2:])):
                data = parser_manager.parse(image)
                self.assertIsInstance(data, PromptInfo)
                self.assertEqual(data.generator, expected_generator)

    def test_parse_missing_file(self):
        parser_manager = ParserManager()
        with self.assertRaises(FileNotFoundError):
            parser_manager.parse(RESOURCE_PATH / "bad_images" / "missing_file.png")

    def test_parse_empty_file(self):
        parser_manager = ParserManager()
        with self.assertRaises(PIL.UnidentifiedImageError):
            parser_manager.parse(RESOURCE_PATH / "bad_images" / "empty_file.png")

    def test_parse_text_string(self):
        parser_manager = ParserManager()
        with self.assertRaises(ValueError):
            with io.StringIO("this is not an image") as file:
                parser_manager.parse(file)

    def test_parse_text_after_idat(self):
        parser_manager = ParserManager()
        result = parser_manager.parse(
            RESOURCE_PATH / "bad_images" / "text_after_idat.png")
        self.assertIsInstance(result, PromptInfo)
