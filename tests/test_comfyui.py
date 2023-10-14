# example image sources:
# https://github.com/comfyanonymous/ComfyUI_examples
import unittest
from collections import namedtuple
from typing import List, Tuple

from PIL import Image

from sdparsers import ComfyUIParser, Model, Prompt, Sampler

from tools import RESOURCE_PATH

IMAGES_FOLDER = RESOURCE_PATH / "comfyui"
ExpectedResult = namedtuple(
    'ExpectedResult', ['num_prompts',
                       'num_models',
                       'num_unique_models',
                       'num_samplers',
                       'num_unique_samplers'])

COMPLEX_WORKFLOWS: List[Tuple[str, ExpectedResult]] = [
    (
        "night_evening_day_morning_cropped.png",
        ExpectedResult(num_prompts=2,
                       num_models=2,
                       num_unique_models=2,
                       num_samplers=2,
                       num_unique_samplers=2)
    ),
    (
        "noisy_latents_3_subjects_cropped.png",
        ExpectedResult(num_prompts=6,
                       num_models=6,
                       num_unique_models=1,
                       num_samplers=6,
                       num_unique_samplers=2)
    ),
    (
        "unclip_2pass_cropped.png",
        ExpectedResult(num_prompts=2,
                       num_models=2,
                       num_unique_models=2,
                       num_samplers=2,
                       num_unique_samplers=2)
    )
]


class ComfyUITester(unittest.TestCase):

    def parse_image(self, filename: str, config=None):
        parser = ComfyUIParser(config)
        with Image.open(IMAGES_FOLDER / filename) as image:
            return parser.parse(image)

    def test_parse(self):
        prompt_info = self.parse_image("img2img_cropped.png")

        self.assertEqual(prompt_info.prompts, [(
            Prompt(
                value="photograph of victorian woman with wings, sky clouds, meadow grass",
                parts=["photograph of victorian woman with wings, sky clouds, meadow grass"],
                weight=None),
            Prompt(
                value="watermark, text",
                parts=["watermark, text"],
                weight=None))])

        self.assertEqual(prompt_info.models, [
            Model(name='v1-5-pruned-emaonly.ckpt', model_hash=None)])

        self.assertEqual(prompt_info.samplers, [
            Sampler(name='sample_dpmpp_2m',
                    parameters={
                        'seed': 280823642470253,
                        'random_seed_after_every_gen': True,
                        'steps': 20,
                        'cfg': 8.0,
                        'scheduler': 'normal',
                        'denoise': 0.8700000000000001})])

    def test_parse_with_config(self):
        config = {
            "sampler_types": [],
            "text_positive_keys": ["text", "positive"],
            "text_negative_keys": ["text", "negative"],
            "fields": {
                "cfg": "cfg_scale"
            }
        }

        prompt_info = self.parse_image("img2img_cropped.png", config)

        self.assertEqual(prompt_info.samplers, [
            Sampler(name='sample_dpmpp_2m',
                    parameters={
                        'seed': 280823642470253,
                        'random_seed_after_every_gen': True,
                        'steps': 20,
                        'cfg_scale': 8.0,
                        'scheduler': 'normal',
                        'denoise': 0.8700000000000001})])

    def test_parse_complex(self):
        for image, expected in COMPLEX_WORKFLOWS:
            with self.subTest(image=image):
                data = self.parse_image(image)

                unique_samplers = {sampler.name for sampler in data.samplers}
                self.assertEqual(len(data.prompts), expected.num_prompts)
                self.assertEqual(len(data.models), expected.num_models)
                self.assertEqual(len(set(data.models)), expected.num_unique_models)
                self.assertEqual(len(data.samplers), expected.num_samplers)
                self.assertEqual(len(unique_samplers), expected.num_unique_samplers)
