import pytest
from PIL import Image
from sd_parsers import Model, Prompt, Sampler
from sd_parsers.parsers import AUTOMATIC1111Parser, _automatic1111

from tests.tools import RESOURCE_PATH

PARAMETERS = (
    "photo of a duck\nNegative prompt: monochrome\n"
    "Steps: 15, Sampler: UniPC, CFG scale: 5, Seed: 235284042, Size: 512x400, "
    "Model hash: c0d1994c73, Model: realistic_realisticVisionV20_v20"
)

MODEL = Model(name="realistic_realisticVisionV20_v20", model_hash="c0d1994c73")
PROMPTS = [Prompt(value="photo of a duck")]
NEGATIVE_PROMPTS = [Prompt(value="monochrome")]

SAMPLER = Sampler(
    name="UniPC",
    parameters={"steps": "15", "cfg_scale": "5", "seed": "235284042"},
    model=MODEL,
    prompts=PROMPTS,
    negative_prompts=NEGATIVE_PROMPTS,
)

testdata = [
    pytest.param(
        "automatic1111_cropped.png",
        (
            SAMPLER,
            set([MODEL]),
            set(PROMPTS),
            set(NEGATIVE_PROMPTS),
            {"size": "512x400"},
        ),
        id="automatic1111_cropped.png",
    ),
    pytest.param(
        "automatic1111_cropped.jpg",
        (
            SAMPLER,
            set([MODEL]),
            set(PROMPTS),
            set(NEGATIVE_PROMPTS),
            {"size": "512x400"},
        ),
        id="automatic1111_cropped.jpg",
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

    parser = AUTOMATIC1111Parser()
    with Image.open(RESOURCE_PATH / "parsers/AUTOMATIC1111" / filename) as image:
        image_data = parser.read_parameters(image)

    assert image_data is not None
    assert image_data.samplers == [expected_sampler]
    assert image_data.prompts == expected_prompts
    assert image_data.negative_prompts == expected_negative_prompts
    assert image_data.models == expected_models
    assert image_data.metadata == expected_metadata


def test_civitai_hashes():
    parameters = PARAMETERS + ', Hashes: {"vae": "c6a580b13a", "model": "c0d1994c73"}'

    info_index, sampler_info, metadata = _automatic1111.get_sampler_info(parameters.split("\n"))

    print(sampler_info)
    print(metadata)
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
        "civitai_hashes": {"model": "c0d1994c73", "vae": "c6a580b13a"},
    }
