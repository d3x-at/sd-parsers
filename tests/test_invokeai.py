import pytest
from PIL import Image
from sd_parsers.data import Prompt
from sd_parsers.parsers import InvokeAIParser
from sd_parsers.parsers._invokeai import _variant_dream

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


def test_split_prompt():
    combined_prompt = "prompt1a, prompt1b, [nprompt1a, nprompt1b], prompt2a, prompt2b, [nprompt2a, nprompt2b], prompt3a"
    output = {}

    _variant_dream._add_prompts(output, combined_prompt, {})

    assert output == {
        "negative_prompts": [
            Prompt(value="nprompt1a, nprompt1b"),
            Prompt(value="nprompt2a, nprompt2b"),
        ],
        "prompts": [
            Prompt(value="prompt1a, prompt1b"),
            Prompt(value="prompt2a, prompt2b"),
            Prompt(value="prompt3a"),
        ],
    }
