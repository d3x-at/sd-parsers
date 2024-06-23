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
        expected_metadata,
    ) = expected

    parser = ComfyUIParser()
    with Image.open(RESOURCE_PATH / "parsers/ComfyUI" / filename) as image:
        params = parser.read_parameters(image)

    samplers, metadata = parser.parse(*params)

    assert samplers == expected_samplers
    assert metadata == expected_metadata
