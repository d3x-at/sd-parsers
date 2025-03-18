import pytest
from PIL import Image
from sd_parsers.extractors import Eagerness, METADATA_EXTRACTORS
from sd_parsers.data import Generators, Prompt
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
        expected_metadata,
    ) = expected

    parser = InvokeAIParser()
    with Image.open(RESOURCE_PATH / "parsers/InvokeAI" / filename) as image:
        assert image.format
        extractor = METADATA_EXTRACTORS[image.format][Eagerness.FAST][0]
        params = extractor(image, parser.generator)
        assert params

    prompt_info = parser.parse(params)

    assert prompt_info.generator == Generators.INVOKEAI
    assert prompt_info.metadata == expected_metadata
    assert prompt_info.samplers == [expected_sampler]


def test_split_prompt():
    combined_prompt = "prompt1a, prompt1b, [nprompt1a, nprompt1b], prompt2a, prompt2b, [nprompt2a, nprompt2b], prompt3a"
    output = {}

    _variant_dream._add_prompts(output, combined_prompt, {})

    assert output == {
        "negative_prompts": [
            Prompt("nprompt1a, nprompt1b", prompt_id="1"),
            Prompt("nprompt2a, nprompt2b", prompt_id="2"),
        ],
        "prompts": [
            Prompt("prompt1a, prompt1b", prompt_id="1"),
            Prompt("prompt2a, prompt2b", prompt_id="2"),
            Prompt("prompt3a", prompt_id="3"),
        ],
    }
