# example image sources:
# https://github.com/comfyanonymous/ComfyUI_examples

import pytest
from PIL import Image
from sd_parsers.data import Generators
from sd_parsers.parsers import ComfyUIParser
from sd_parsers.extractors import METADATA_EXTRACTORS, Eagerness

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
        assert image.format
        extractor = METADATA_EXTRACTORS[image.format][Eagerness.FAST][0]
        params = extractor(image, parser.generator)
        assert params

    generator, samplers, metadata = parser.parse(params)

    assert generator == Generators.COMFYUI
    assert samplers == expected_samplers
    assert metadata == expected_metadata
