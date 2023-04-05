import re
from typing import Dict, List, Tuple

from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo

GENERATOR_ID = "AUTOMATIC1111"


class AUTOMATIC1111Parser(Parser):
    '''parse images created in AUTOMATIC1111's webui'''
    re_param_code = r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)'
    re_param = re.compile(re_param_code)

    def parse(self, image):
        parameters = image.info.get('parameters')
        if parameters is None:
            return None

        lines, metadata = self._prepare_metadata(parameters.split("\n"))
        if not metadata:
            return None

        prompt = self._get_prompt(lines)
        return PromptInfo(GENERATOR_ID, [prompt], metadata,
                          {"parameters": parameters})

    def _prepare_metadata(self, lines: List[str]) -> Tuple[List[str], Dict[str, str]]:
        '''attempt to read metadata tags from the parametes lines'''
        parts = self.re_param.findall(lines[-1].strip())
        if len(parts) < 3:
            return lines, []

        metadata = self.process_metadata((k, v.strip("\"")) for k, v in parts)
        return lines[:-1], metadata

    @staticmethod
    def _get_prompt(lines: List[str]):
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

        return Prompt("\n".join(prompt)), Prompt("\n".join(negative_prompt))
