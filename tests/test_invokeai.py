import pytest
from PIL import Image
from sd_parsers import Model, Prompt, Sampler
from sd_parsers.parsers import InvokeAIParser

from tests.tools import RESOURCE_PATH

MODEL = Model(
    name="deliberateForInvoke_v08",
    model_hash="56d1442a0feefd64836a19ac8e3527ec71c884fc962e246ddf67b03e42921272",
)
PROMPTS = [
    Prompt(
        value=(
            "professional full body photo of young woman, "
            "hyper long brunette hair, elegant hair, "
            "wearing a bikini top and asymmetric short skirt, "
            "curvy body, long legs, (imperfect skin), detailed skin, "
            "intense freckles, super long eye lashes, at night, outside, "
            "city background, 8k ultra detailed, realistic, high quality, "
            "film grain, low contrast"
        ),
        weight=1.0,
    )
]

NEGATIVE_PROMPTS = [
    Prompt(
        value="rendering, glowing eyes, skinny",
        weight=1.0,
    )
]

testdata = [
    pytest.param(
        "invokeai1_cropped.png",
        (
            Sampler(
                name="k_lms",
                parameters={
                    "steps": 50,
                    "cfg_scale": 5,
                    "threshold": 0,
                    "perlin": 0,
                    "seed": 2980747362,
                },
                model=MODEL,
                prompts=PROMPTS,
                negative_prompts=NEGATIVE_PROMPTS,
            ),
            set([MODEL]),
            set(PROMPTS),
            set(NEGATIVE_PROMPTS),
            {
                "model": "stable diffusion",
                "app_id": "invoke-ai/InvokeAI",
                "app_version": "2.3.0",
                "height": 768,
                "width": 512,
                "size": "512x768",
                "seamless": False,
                "hires_fix": False,
                "type": "txt2img",
                "postprocessing": [
                    {"type": "codeformer", "strength": 0.9, "fidelity": 0.75},
                    {"type": "esrgan", "scale": 4, "strength": 0.95},
                ],
                "variations": [],
            },
        ),
        id="invokeai1_cropped.png",
    ),
]


@pytest.mark.parametrize("filename, expected", testdata)
def test_parse(filename: str, expected):
    (
        expected_sampler,
        expected_models,
        expected_prompts,
        expected_negative_prompts,
        expected_metadata,
    ) = expected

    parser = InvokeAIParser()
    with Image.open(RESOURCE_PATH / "parsers/InvokeAI" / filename) as image:
        image_data, error = parser.read_parameters(image)

    assert image_data is not None
    assert error is None
    assert image_data.samplers == [expected_sampler]
    assert image_data.prompts == expected_prompts
    assert image_data.negative_prompts == expected_negative_prompts
    assert image_data.models == expected_models
    assert image_data.metadata == expected_metadata
