import unittest

from PIL import Image

from sdparsers import Model, Prompt, PromptInfo, Sampler
from sdparsers.parsers import AUTOMATIC1111Parser, AUTOMATICStealthParser

from tools import RESOURCE_PATH

IMAGES_FOLDER = RESOURCE_PATH / "automatic1111"
OUTPUT = PromptInfo(
    generator='AUTOMATIC1111',
    prompts=[(
        Prompt(value='photo of a duck',
               parts=['photo of a duck'],
               weight=None),
        Prompt(value='monochrome',
               parts=['monochrome'],
               weight=None)
    )],
    samplers=[
        Sampler(name='UniPC',
                parameters={'steps': '15', 'cfg_scale': '5', 'seed': '235284042'})
    ],
    models=[
        Model(name='realistic_realisticVisionV20_v20',
              model_hash='c0d1994c73')
    ],
    metadata={'size': '512x400'},
    raw_params={'parameters': (
        "photo of a duck\nNegative prompt: monochrome\n"
        "Steps: 15, Sampler: UniPC, CFG scale: 5, Seed: 235284042, Size: 512x400, "
        "Model hash: c0d1994c73, Model: realistic_realisticVisionV20_v20"
    )})


class Automatic1111Tester(unittest.TestCase):

    def parse_image(self, filename: str, config=None):
        parser = AUTOMATIC1111Parser(config)
        with Image.open(IMAGES_FOLDER / filename) as image:
            return parser.parse(image)

    def parse_stealth_image(self, filename: str, config=None):
        parser = AUTOMATICStealthParser(config)
        with Image.open(IMAGES_FOLDER / filename) as image:
            return parser.parse(image)

    def test_parse_png(self):
        prompt_info = self.parse_image("automatic1111_cropped.png")
        self.assertEqual(prompt_info, OUTPUT)

    def test_parse_jpg(self):
        prompt_info = self.parse_image("automatic1111_cropped.jpg")
        self.assertEqual(prompt_info, OUTPUT)

    def test_parse_stealth(self):
        prompt_info = self.parse_stealth_image("automatic1111_stealth.png")
        self.assertEqual(prompt_info, OUTPUT)
