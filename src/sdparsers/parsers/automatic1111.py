import re
from typing import Dict, List, Tuple

from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo

GENERATOR_ID = "AUTOMATIC1111"


class AUTOMATIC1111Parser(Parser):
    '''parse images created in AUTOMATIC1111's webui'''
    RE_PARAM = re.compile(
        r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)')

    def parse(self, image):
        parameters = image.info.get('parameters')
        if parameters is None:
            return None

        prompt, metadata = AUTOMATIC1111Parser._prepare_metadata(parameters)
        if not metadata:
            return None

        return PromptInfo(GENERATOR_ID, [prompt],
                          self.process_metadata(metadata),
                          {"parameters": parameters})

    @classmethod
    def _prepare_metadata(cls, parameters: str) -> Tuple[Tuple[Prompt, Prompt], List[Tuple[str, str]]]:

        def get_metadata(parameters):
            lines = parameters.split("\n")
            metadata = cls.RE_PARAM.findall(lines[-1].strip())
            if len(metadata) < 3:
                return lines, []
            return lines[:-1], metadata

        lines, metadata = get_metadata(parameters)
        prompt, negative_prompt = [], []
        i = 0

        # prompt
        for line in lines:
            line = line.strip()
            if line.startswith("Negative prompt:"):
                lines[i] = line[16:]
                break
            prompt.append(line)
            i += 1

        # negative prompt
        for line in lines[i:]:
            negative_prompt.append(line.strip())

        return (Prompt("\n".join(prompt)), Prompt("\n".join(negative_prompt))), metadata
