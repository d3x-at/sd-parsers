import unittest

from PIL import Image

from sdparsers import Model, Prompt, PromptInfo, Sampler
from sdparsers.parsers import NovelAIParser

from tools import RESOURCE_PATH

IMAGES_FOLDER = RESOURCE_PATH / "novelai"
OUTPUT = PromptInfo(
    generator='NovelAI',
    prompts=[(
        Prompt(value='masterpiece, best quality,  cat, space, icon',
               parts=['masterpiece, best quality,  cat, space, icon'],
               weight=None),
        Prompt(value=("lowres, bad anatomy, bad hands, text, error, missing fingers, "
                      "extra digit, fewer digits, cropped, worst quality, low quality, "
                      "normal quality, jpeg artifacts, signature, watermark, username, "
                      "blurry, lowres, bad anatomy, bad hands, text, error, missing fingers, "
                      "extra digit, fewer digits, cropped, worst quality, low quality, "
                      "normal quality, jpeg artifacts, signature, watermark, username, blurry"),
               parts=[("lowres, bad anatomy, bad hands, text, error, missing fingers, "
                      "extra digit, fewer digits, cropped, worst quality, low quality, "
                       "normal quality, jpeg artifacts, signature, watermark, username, "
                       "blurry, lowres, bad anatomy, bad hands, text, error, missing fingers, "
                       "extra digit, fewer digits, cropped, worst quality, low quality, "
                       "normal quality, jpeg artifacts, signature, watermark, username, blurry")],
               weight=None))],
    samplers=[
        Sampler(name='k_euler_ancestral',
                parameters={'seed': 2253955223, 'strength': 0.4, 'scale': 10.0})],
    models=[
        Model(name='Stable Diffusion', model_hash='1D44365E')],
    metadata={'steps': 50},
    raw_params={'Comment': ('{"steps": 50, "sampler": "k_euler_ancestral", "seed": 2253955223, '
                            '"strength": 0.4, "noise": 0.0, "scale": 10.0, "uc": "lowres, '
                            'bad anatomy, bad hands, text, error, missing fingers, extra digit, '
                            'fewer digits, cropped, worst quality, low quality, normal quality, '
                            'jpeg artifacts, signature, watermark, username, blurry, lowres, '
                            'bad anatomy, bad hands, text, error, missing fingers, extra digit, '
                            'fewer digits, cropped, worst quality, low quality, normal quality, '
                            'jpeg artifacts, signature, watermark, username, blurry"}'),
                'Description': 'masterpiece, best quality,  cat, space, icon',
                'Software': 'NovelAI',
                'Source': 'Stable Diffusion 1D44365E'})


class NovelAITester(unittest.TestCase):

    def parse_image(self, filename: str, config: dict = None):
        parser = NovelAIParser(config)
        with Image.open(IMAGES_FOLDER / filename) as image:
            return parser.parse(image)

    def test_parse(self):
        prompt_info = self.parse_image("novelai1_cropped.png")
        self.assertEqual(prompt_info, OUTPUT)
