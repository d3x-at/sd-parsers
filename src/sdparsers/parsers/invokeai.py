import json
import re
from itertools import chain

from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo

GENERATOR_ID = "InvokeAI"


class InvokeAIParser(Parser):
    re_prompt_negatives = re.compile('\[([^\[]*)\]')

    def parse(self, image):
        params_metadata = image.info.get('sd-metadata')
        if not params_metadata:
            return None

        raw_params = {'sd-metadata': params_metadata}
        params_dream = image.info.get('Dream')
        if params_dream:
            raw_params['Dream'] = params_dream

        prompts, metadata = self._prepare_metadata(params_metadata)
        return PromptInfo(GENERATOR_ID, prompts, metadata, raw_params)

    def _prepare_metadata(self, params_metadata):
        metadata = json.loads(params_metadata)

        def split_prompt(prompt: str, weight: float):
            negatives = map(str.strip, self.re_prompt_negatives.findall(prompt))
            positive = self.re_prompt_negatives.sub('', prompt).strip()
            return (Prompt(positive), Prompt(', '.join(negatives)), weight)

        prompts = [split_prompt(prompt["prompt"], float(prompt["weight"]))
                   for prompt in metadata['image']['prompt']]

        return prompts, self.process_metadata(chain(
            ((k, v) for k, v in metadata.items() if k != 'image'),
            ((k, v) for k, v in metadata['image'].items() if k != "prompt")))
