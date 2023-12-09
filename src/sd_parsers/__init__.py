"""
A library to read metadata from images created with Stable Diffusion.

Find more information at: https://github.com/d3x-at/sd-parsers

Basic usage:
-------------
from sd_parsers import ParserManager

parser_manager = ParserManager()

prompt_info = parser_manager.parse("image.png")

if prompt_info is not None:
    for prompt in prompt_info.prompts:
        print(prompt.value)

"""
from ._models import Model, Prompt, Sampler
from ._parser import Generators, Parser
from ._parser_manager import ParserManager
from ._prompt_info import PromptInfo

__all__ = [
    "Parser",
    "Generators",
    "ParserManager",
    "PromptInfo",
    "Model",
    "Prompt",
    "Sampler",
]
