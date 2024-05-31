import pytest
from PIL import Image
from sd_parsers import Model, Prompt, Sampler
from sd_parsers.parsers import NovelAIParser

from tests.tools import RESOURCE_PATH

MODEL = Model(name="Stable Diffusion", model_hash="1D44365E")
PROMPTS = [Prompt(value="masterpiece, best quality,  cat, space, icon")]
NEGATIVE_PROMPTS = [
    Prompt(
        value=(
            "lowres, bad anatomy, bad hands, text, error, missing fingers, "
            "extra digit, fewer digits, cropped, worst quality, low quality, "
            "normal quality, jpeg artifacts, signature, watermark, username, "
            "blurry, lowres, bad anatomy, bad hands, text, error, missing fingers, "
            "extra digit, fewer digits, cropped, worst quality, low quality, "
            "normal quality, jpeg artifacts, signature, watermark, username, blurry"
        )
    )
]

testdata = [
    pytest.param(
        "novelai1_cropped.png",
        (
            Sampler(
                name="k_euler_ancestral",
                parameters={"seed": 2253955223, "strength": 0.4, "noise": 0.0, "scale": 10.0},
                model=Model(name="Stable Diffusion", model_hash="1D44365E"),
                prompts=PROMPTS,
                negative_prompts=NEGATIVE_PROMPTS,
            ),
            set([MODEL]),
            set(PROMPTS),
            set(NEGATIVE_PROMPTS),
            {"steps": 50},
        ),
        id="novelai1_cropped.png",
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

    parser = NovelAIParser()
    with Image.open(RESOURCE_PATH / "parsers/NovelAI" / filename) as image:
        image_data = parser.read_parameters(image)

    assert image_data is not None
    assert image_data.samplers == [expected_sampler]
    assert image_data.prompts == expected_prompts
    assert image_data.negative_prompts == expected_negative_prompts
    assert image_data.models == expected_models
    assert image_data.metadata == expected_metadata
