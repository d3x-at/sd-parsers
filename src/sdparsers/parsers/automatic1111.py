import re
from typing import List, Tuple

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

        lines, processing_info = self._prepare_processing_info(
            parameters.split("\n"))
        if not processing_info:
            return None

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

        return PromptInfo(GENERATOR_ID, [(
            Prompt("\n".join(prompt)),
            Prompt("\n".join(negative_prompt)))],
            processing_info,
            {"parameters": parameters})

    def _prepare_processing_info(self, lines: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
        '''attempt to read processing info tags from the parametes lines'''
        parts = self.re_param.findall(lines[-1].strip())
        if len(parts) < 3:
            return lines, []

        processing_info = self.process_items(
            (k, v.strip("\"")) for k, v in parts)

        return lines[:-1], processing_info
