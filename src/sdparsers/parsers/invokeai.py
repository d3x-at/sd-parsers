import json
import re
from itertools import chain

from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo

GENERATOR_ID = "InvokeAI"


class InvokeAIParser(Parser):
    re_prompt = re.compile(r'^(.*?)(?:\[([^\[]*)\])?$')

    def parse(self, image):
        params_metadata = image.info.get('sd-metadata')
        if not params_metadata:
            return None

        prompts, processing_info = self.extract_prompts(params_metadata)
        if not prompts:
            return None

        raw_params = {'sd-metadata': params_metadata}
        params_dream = image.info.get('Dream')
        if params_dream:
            raw_params['Dream'] = params_dream

        return PromptInfo(GENERATOR_ID,
                          prompts,
                          processing_info,
                          raw_params)

    def extract_prompts(self, params_metadata):
        metadata = json.loads(params_metadata)

        # prompts
        prompts = []
        for item in metadata['image']['prompt']:
            match = self.re_prompt.fullmatch(item['prompt'])
            if match:
                prompt = negative_prompt = ""
                if match[1] != "":
                    prompt = Prompt(match[1].strip())
                if match[2] != "":
                    negative_prompt = Prompt(match[2])
                prompts.append((prompt, negative_prompt))

        # processing-infos
        processing_info = self.process_items(chain(
            ((k, v) for k, v in metadata.items() if k != 'image'),
            ((k, v) for k, v in metadata['image'].items() if k != "prompt")))

        return prompts, processing_info
