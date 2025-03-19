"""Example stub for additional parsers"""

from typing import Any, Dict

from sd_parsers.data import Generators, Model, Prompt, Sampler, PromptInfo
from sd_parsers.exceptions import ParserError

from ._parser import Parser


class DummyParser(Parser):
    """
    Example stub for additional parsers
    """

    generator = Generators.UNKNOWN

    def parse(self, parameters: Dict[str, Any]) -> PromptInfo:
        """
        Process the generation parameters returned by `read_parameters()`.

        Make sure that the original parameters data does not get altered in the process of parsing.

        Raise a `ParserError` when something goes wrong.
        """

        working_parameters = dict(parameters)

        try:
            sampler_name = working_parameters.pop("sampler name")

            sampler = Sampler(
                name=sampler_name,
                parameters={
                    "info": "a dict of sampler-specific parameters, i.e.:",
                    "cfg_scale": 1.2,
                    "seed": 1234,
                    "steps": 5,
                },
                model=Model("name of the used checkpoint", "hash value of the checkpoint"),
                prompts=[
                    Prompt("positive prompt"),
                ],
                negative_prompts=[
                    Prompt("negative prompt"),
                ],
            )
        except Exception as error:
            raise ParserError("something happened here") from error

        # return list of samplers and unused working parameters
        return PromptInfo(self.generator, [sampler], working_parameters, parameters)
