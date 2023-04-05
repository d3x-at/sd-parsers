import json
from typing import Optional

from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo

GENERATOR_ID = "ComfyUI"
SAMPLER_TYPES = ("KSampler", "KSamplerAdvanced")
TEXT_TYPES = ("CLIPTextEncode")


class ComfyUIParser(Parser):

    def parse(self, image):
        params_prompt = image.info.get('prompt')
        params_workflow = image.info.get('workflow')
        if not params_prompt or not params_workflow:
            return None

        prompts, metadata = self._prepare_metadata(
            params_prompt, params_workflow)

        return PromptInfo(GENERATOR_ID, prompts, metadata, {
            "prompt": params_prompt,
            "workflow": params_workflow
        })

    def _prepare_metadata(self, params_prompt: str, params_workflow: str):
        prompt_data = json.loads(params_prompt)

        def get_input_id(node, type: str):
            try:
                return node['inputs'][type][0]
            except KeyError:
                return None

        def get_prompt(node_id) -> Optional[str]:
            if node_id is None:
                return None

            node = prompt_data[node_id]
            if node['class_type'] in TEXT_TYPES:
                return Prompt(node['inputs']['text'].strip())
            return None

        # check all sampler types for inputs
        prompt_ids = []
        for node in prompt_data.values():
            if node['class_type'] not in SAMPLER_TYPES:
                continue

            prompt_ids.append((get_input_id(node, "positive"),
                              get_input_id(node, "negative")))

        # ignore multiple uses
        prompts = []
        for positive_id, negative_id in set(prompt_ids):
            positive_prompt = get_prompt(positive_id)
            negative_prompt = get_prompt(negative_id)
            if positive_prompt or negative_prompt:
                prompts.append((positive_prompt, negative_prompt))

        return prompts, {
            "prompt": prompt_data,
            "workflow": json.loads(params_workflow)
        }
