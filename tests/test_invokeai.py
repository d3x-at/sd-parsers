import unittest

from PIL import Image

from sdparsers import InvokeAIParser, Model, Prompt, Sampler

from tools import RESOURCE_PATH

IMAGES_FOLDER = RESOURCE_PATH / "invokeai"


class InvokeAITester(unittest.TestCase):

    def parse_image(self, filename: str, config: dict = None):
        parser = InvokeAIParser(config)
        with Image.open(IMAGES_FOLDER / filename) as image:
            return parser.parse(image)

    def test_parse(self):
        prompt_info = self.parse_image("invokeai1_cropped.png")

        self.assertEqual(prompt_info.prompts, [(
            Prompt(
                value=("professional full body photo of young woman, "
                       "hyper long brunette hair, elegant hair, "
                       "wearing a bikini top and asymmetric short skirt, "
                       "curvy body, long legs, (imperfect skin), detailed skin, "
                       "intense freckles, super long eye lashes, at night, outside, "
                       "city background, 8k ultra detailed, realistic, high quality, "
                       "film grain, low contrast"),
                parts=["professional full body photo of young woman, "
                       "hyper long brunette hair, elegant hair, "
                       "wearing a bikini top and asymmetric short skirt, "
                       "curvy body, long legs, (imperfect skin), detailed skin, "
                       "intense freckles, super long eye lashes, at night, outside, "
                       "city background, 8k ultra detailed, realistic, high quality, "
                       "film grain, low contrast"],
                weight=1.0),
            Prompt(
                value='rendering, glowing eyes, skinny',
                parts=['rendering, glowing eyes, skinny'],
                weight=1.0))])

        self.assertEqual(prompt_info.models, [
            Model(name='deliberateForInvoke_v08',
                  model_hash='56d1442a0feefd64836a19ac8e3527ec71c884fc962e246ddf67b03e42921272')])

        self.assertEqual(prompt_info.samplers, [
            Sampler(name='k_lms',
                    parameters={'steps': 50, 'cfg_scale': 5, 'threshold': 0,
                                'perlin': 0, 'seed': 2980747362})])

        self.assertEqual(prompt_info.metadata, {
            'model': 'stable diffusion',
            'app_id': 'invoke-ai/InvokeAI',
            'app_version': '2.3.0',
            'height': 768,
            'width': 512,
            'seamless': False,
            'hires_fix': False,
            'type': 'txt2img',
            'postprocessing': [
                {'type': 'codeformer', 'strength': 0.9, 'fidelity': 0.75},
                {'type': 'esrgan', 'scale': 4, 'strength': 0.95}],
            'variations': []})

    def test_parse_with_config(self):
        config = {
            "fields": {
                "size": {
                    "values": [
                        "width",
                        "height"
                    ],
                    "format": "{width}x{height}"
                }
            }
        }

        data = self.parse_image("invokeai1_cropped.png", config)
        self.assertIn("size", data.metadata)
        self.assertNotIn("width", data.metadata)
        self.assertNotIn("height", data.metadata)
        self.assertEqual(data.metadata["size"], "512x768")
