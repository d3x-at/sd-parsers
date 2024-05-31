# example image sources:
# https://github.com/comfyanonymous/ComfyUI_examples

import pytest
from PIL import Image
from sd_parsers.parsers import ComfyUIParser

from tests.resources.parsers.ComfyUI import img2img_cropped, night_evening_day_morning_cropped
from tests.tools import RESOURCE_PATH

testdata = [
    img2img_cropped.PARAM,
    night_evening_day_morning_cropped.PARAM,
]


@pytest.mark.parametrize("filename, expected", testdata)
def test_parse(filename: str, expected):
    (
        expected_samplers,
        expected_models,
        expected_prompts,
        expected_negative_prompts,
        expected_metadata,
    ) = expected

    parser = ComfyUIParser()
    with Image.open(RESOURCE_PATH / "parsers/ComfyUI" / filename) as image:
        image_data = parser.read_parameters(image)

    assert image_data is not None
    assert image_data.samplers == expected_samplers
    assert image_data.prompts == expected_prompts
    assert image_data.negative_prompts == expected_negative_prompts
    assert image_data.models == expected_models
    assert image_data.metadata == expected_metadata
