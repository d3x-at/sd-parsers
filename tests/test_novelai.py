import pytest
from PIL import Image
from sd_parsers.extractors import Eagerness, METADATA_EXTRACTORS
from sd_parsers.data import Generators, Model, Prompt, Sampler
from sd_parsers.parsers import NovelAIParser

from tests.tools import RESOURCE_PATH

testdata = [
    pytest.param(
        "novelai1_cropped.png",
        (
            [
                Sampler(
                    name="k_euler_ancestral",
                    parameters={
                        "seed": 2253955223,
                        "strength": 0.4,
                        "noise": 0.0,
                        "cfg_scale": 10.0,
                    },
                    model=Model(name="Stable Diffusion", hash="1D44365E"),
                    prompts=[Prompt("masterpiece, best quality,  cat, space, icon")],
                    negative_prompts=[
                        Prompt(
                            (
                                "lowres, bad anatomy, bad hands, text, error, missing fingers, "
                                "extra digit, fewer digits, cropped, worst quality, low quality, "
                                "normal quality, jpeg artifacts, signature, watermark, username, "
                                "blurry, lowres, bad anatomy, bad hands, text, error, missing fingers, "
                                "extra digit, fewer digits, cropped, worst quality, low quality, "
                                "normal quality, jpeg artifacts, signature, watermark, username, blurry"
                            ),
                        )
                    ],
                )
            ],
            {"steps": 50},
        ),
        id="novelai1_cropped.png",
    ),
]


@pytest.mark.parametrize("filename, expected", testdata)
def test_parse(filename: str, expected):
    (
        expected_samplers,
        expected_metadata,
    ) = expected

    parser = NovelAIParser()
    with Image.open(RESOURCE_PATH / "parsers/NovelAI" / filename) as image:
        assert image.format
        extractor = METADATA_EXTRACTORS[image.format][Eagerness.FAST][0]
        params = extractor(image, parser.generator)
        assert params

    prompt_info = parser.parse(params)

    assert prompt_info.generator == Generators.NOVELAI
    assert prompt_info.samplers == expected_samplers
    assert prompt_info.metadata == expected_metadata
