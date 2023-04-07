import json
import typing
from collections import defaultdict

from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo

GENERATOR_ID = "ComfyUI"
SAMPLER_TYPES_DEFAULT = ["KSampler", "KSamplerAdvanced"]
TEXT_TYPES_DEFAULT = ["CLIPTextEncode"]
TRAVERSE_TYPES_DEFAULT = ["CONDITIONING"]
TRAVERSE_LIMIT_DEFAULT = 100


class ComfyUIParser(Parser):

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)

        self.sampler_types = self.config.get("sampler_types", SAMPLER_TYPES_DEFAULT)
        self.text_types = self.config.get("text_types", TEXT_TYPES_DEFAULT)
        self.traverse_types = self.config.get("traverse_types", TRAVERSE_TYPES_DEFAULT)
        self.traverse_limit = self.config.get("traverse_limit", TRAVERSE_LIMIT_DEFAULT)

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
        workflow_data = json.loads(params_workflow)

        links = defaultdict(list)
        for _, output_id, _, input_id, _, link_type in workflow_data["links"]:
            if link_type in self.traverse_types:
                links[input_id].append(output_id)

        def get_prompts(input_id: typing.Optional[int], depth: int = 0) -> typing.Iterable[str]:
            '''recursively search for a text prompt, starting from the given node id'''
            if input_id is None or \
                    (self.traverse_limit != -1 and depth >= self.traverse_limit):
                return None
            try:
                node = prompt_data[str(input_id)]
                if node['class_type'] in self.text_types:
                    yield node['inputs']['text'].strip()

                for output_id in links[input_id]:
                    yield from get_prompts(output_id, depth + 1)
            except (TypeError, KeyError):
                return None

        # check all sampler types for inputs
        prompt_ids = []
        for node in prompt_data.values():
            if node['class_type'] not in self.sampler_types:
                continue

            positive_id = int(node['inputs']["positive"][0]) \
                if node['inputs']["positive"] else None
            negative_id = int(node['inputs']["negative"][0]) \
                if node['inputs']["negative"] else None

            prompt_ids.append((positive_id, negative_id))

        # ignore multiple uses
        prompts = []
        for positive_id, negative_id in set(prompt_ids):
            positive_prompts = list(get_prompts(positive_id))
            negative_prompts = list(get_prompts(negative_id))
            if negative_prompts or positive_prompts:
                prompts.append((
                    Prompt(value=",\n".join(positive_prompts), parts=positive_prompts)
                    if positive_prompts else None,
                    Prompt(value=",\n".join(negative_prompts), parts=negative_prompts)
                    if negative_prompts else None
                ))

        return prompts, {
            "prompt": prompt_data,
            "workflow": workflow_data
        }
