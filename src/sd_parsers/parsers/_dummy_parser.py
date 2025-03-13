"""Example stub for additional parsers"""

from typing import Any, Dict

from sd_parsers.data import Generators, Model, Prompt, Sampler
from sd_parsers.exceptions import ParserError
from sd_parsers.parser import Parser, ParseResult


class DummyParser(Parser):
    """
    Example stub for additional parsers
    """

    generator = Generators.UNKNOWN

    def parse(self, parameters: Dict[str, Any]) -> ParseResult:
        """
        Process the generation parameters returned by `read_parameters()`.

        Make sure that the original parameters data does not get altered in the process of parsing.

        Raise a `ParserError` when something goes wrong.
        """

        working_parameters = dict(parameters)

        try:
            sampler = {
                "name": working_parameters.pop("sampler name"),
                "parameters": "a dict of sampler-specific parameters, i.e.: cfg scale, seed, steps, ...",
                "model": Model("name of the used checkpoint", "hash value of the checkpoint"),
                "prompts": [
                    Prompt(1, "positive prompt"),
                ],
                "negative_prompts": [
                    Prompt(2, "negative prompt"),
                    Prompt(3, "keep prompt ids unique"),
                ],
            }
        except Exception as error:
            raise ParserError("something happened here") from error

        # return list of samplers and unused working parameters
        return self.generator, [Sampler(**sampler)], working_parameters
