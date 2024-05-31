import pytest
from PIL import Image
from sd_parsers.parsers import InvokeAIParser

from tests.resources.parsers.InvokeAI import invokeai_dream1, invokeai_imeta1, invokeai_sdmeta1
from tests.tools import RESOURCE_PATH

testdata = [
    invokeai_sdmeta1.PARAM,
    invokeai_imeta1.PARAM,
    invokeai_dream1.PARAM,
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
        image_data = parser.read_parameters(image)

    assert image_data is not None

    assert image_data.prompts == expected_prompts
    assert image_data.negative_prompts == expected_negative_prompts
    assert image_data.models == expected_models
    assert image_data.metadata == expected_metadata
    assert image_data.samplers == [expected_sampler]
