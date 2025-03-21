import pytest
from PIL import Image
from sd_parsers.data import Model, Prompt, Sampler, Generators
from sd_parsers.parsers import AUTOMATIC1111Parser, _automatic1111
from sd_parsers.extractors import Eagerness, METADATA_EXTRACTORS

from tests.tools import RESOURCE_PATH

PARAMETERS = (
    "photo of a duck\nNegative prompt: monochrome\n"
    "Steps: 15, Sampler: UniPC, CFG scale: 5, Seed: 235284042, Size: 512x400, "
    "Model hash: c0d1994c73, Model: realistic_realisticVisionV20_v20"
)

SAMPLERS = [
    Sampler(
        name="UniPC",
        parameters={"steps": "15", "cfg_scale": "5", "seed": "235284042"},
        model=Model(name="realistic_realisticVisionV20_v20", hash="c0d1994c73"),
        prompts=[Prompt("photo of a duck")],
        negative_prompts=[Prompt("monochrome")],
    )
]

testdata = [
    pytest.param(
        "automatic1111_cropped.png",
        (
            SAMPLERS,
            {"Size": "512x400"},
        ),
        id="automatic1111_cropped.png",
    ),
    pytest.param(
        "automatic1111_cropped.jpg",
        (
            SAMPLERS,
            {"Size": "512x400"},
        ),
        id="automatic1111_cropped.jpg",
    ),
]


@pytest.mark.parametrize("filename, expected", testdata)
def test_parse(filename: str, expected):
    expected_samplers, expected_metadata = expected

    parser = AUTOMATIC1111Parser()
    with Image.open(RESOURCE_PATH / "parsers/AUTOMATIC1111" / filename) as image:
        assert image.format
        extractor = METADATA_EXTRACTORS[image.format][Eagerness.FAST][0]
        params = extractor(image, parser.generator)
        assert params

    prompt_info = parser.parse(params)

    assert prompt_info.generator == Generators.AUTOMATIC1111
    assert prompt_info.samplers == expected_samplers
    assert prompt_info.metadata == expected_metadata


def test_hashes():
    parameters = PARAMETERS + ', Hashes: {"vae": "c6a580b13a", "model": "c0d1994c73"}'

    info_index, sampler_info, metadata = _automatic1111._get_sampler_info(parameters.split("\n"))

    assert info_index == 2
    assert sampler_info == {
        "CFG scale": "5",
        "Sampler": "UniPC",
        "Seed": "235284042",
        "Steps": "15",
    }
    assert metadata == {
        "Model": "realistic_realisticVisionV20_v20",
        "Model hash": "c0d1994c73",
        "Size": "512x400",
        "Hashes": {"model": "c0d1994c73", "vae": "c6a580b13a"},
    }
