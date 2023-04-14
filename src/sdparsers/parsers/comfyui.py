import json
import typing
from collections import defaultdict

from ..parser import Parser
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

SAMPLER_TYPES_DEFAULT = ["KSampler", "KSamplerAdvanced"]
TEXT_TYPES_DEFAULT = []  # by default, don't filter text nodes by class_type
TRAVERSE_TYPES_DEFAULT = ["CONDITIONING"]
TRAVERSE_LIMIT_DEFAULT = 100

_SAMPLER_EXCLUDES = ['sampler_name', 'model', 'positive', 'negative', 'latent_image']


class ComfyUIParser(Parser):
    GENERATOR_ID = "ComfyUI"

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

        prompts, samplers, models = self._prepare_metadata(params_prompt, params_workflow)

        return PromptInfo(self.GENERATOR_ID, prompts, samplers, models, {}, {
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
                return
            try:
                node = prompt_data[str(input_id)]
                if node['class_type'] in self.text_types or \
                        (not self.text_types and "text" in node['inputs']):
                    yield node['inputs']['text'].strip()
                for output_id in links[input_id]:
                    yield from get_prompts(output_id, depth + 1)
            except KeyError:
                return

        # check all sampler types
        samplers = []
        models = []
        prompt_ids = []
        for node in prompt_data.values():
            if node['class_type'] not in self.sampler_types:
                continue
            inputs = node['inputs']

            sampler_params = ((key, value) for key, value in inputs.items()
                              if key not in _SAMPLER_EXCLUDES)
            sampler = Sampler(
                name=inputs.get('sampler_name'),
                parameters=self._process_metadata(sampler_params))
            samplers.append(sampler)

            if inputs['model']:
                model_node = prompt_data[inputs['model'][0]]
                model = Model(name=model_node['inputs'].get('ckpt_name'))
                models.append(model)

            positive_id = int(inputs["positive"][0]) \
                if inputs["positive"] else None
            negative_id = int(inputs["negative"][0]) \
                if inputs["negative"] else None

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

        return prompts, samplers, models
