import json
from collections import defaultdict
from typing import Any, Iterable, Optional, Set, Tuple

from ..parser import Parser
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

SAMPLER_TYPES_DEFAULT = ["KSampler", "KSamplerAdvanced"]
TEXT_TYPES_DEFAULT = []  # by default, don't filter text nodes by class_type
TEXT_POSITIVE_KEYS_DEFAULT = ['text']
TEXT_NEGATIVE_KEYS_DEFAULT = ['text']
TRAVERSE_TYPES_DEFAULT = ["CONDITIONING"]
TRAVERSE_LIMIT_DEFAULT = 100

_SAMPLER_EXCLUDES = ['sampler_name', 'model', 'positive', 'negative', 'latent_image']


class ComfyUIParser(Parser):
    GENERATOR_ID = "ComfyUI"

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)

        self.sampler_types = self.config.get("sampler_types", SAMPLER_TYPES_DEFAULT)
        self.traverse_types = self.config.get("traverse_types", TRAVERSE_TYPES_DEFAULT)
        self.traverse_limit = self.config.get("traverse_limit", TRAVERSE_LIMIT_DEFAULT)

        self.text_types = self.config.get("text_types", TEXT_TYPES_DEFAULT)
        self.text_positive_keys = set(self.config.get("text_positive_keys",
                                                      TEXT_POSITIVE_KEYS_DEFAULT))
        self.text_negative_keys = set(self.config.get("text_negative_keys",
                                                      TEXT_NEGATIVE_KEYS_DEFAULT))

    def parse(self, image):
        if image.format != "PNG":
            return None

        params_prompt = image.text.get('prompt')
        params_workflow = image.text.get('workflow')
        if not params_prompt or not params_workflow:
            return None

        image_data = {
            'prompt': json.loads(params_prompt),
            'workflow': json.loads(params_workflow),
            'links': defaultdict(list),
            'inputs_cache': {'uniq': set()}
        }

        # build list of links of the allowed traverse types
        # (start at a sampler, go backwards to reach all available model and text nodes)
        try:
            for _, output_id, _, input_id, _, link_type in image_data['workflow']["links"]:
                if link_type in self.traverse_types:
                    image_data['links'][input_id].append(output_id)
        except ValueError:
            pass

        metadata = self._prepare_metadata(image_data)

        return PromptInfo(self.GENERATOR_ID, **metadata, raw_params={
            "prompt": params_prompt,
            "workflow": params_workflow
        })

    def _prepare_metadata(self, image_data: dict):

        def might_be_sampler(node):
            try:
                if self.sampler_types:
                    return node['class_type'] in self.sampler_types
                return all(key in node['inputs'].keys() for key in _SAMPLER_EXCLUDES)
            except KeyError:
                return False

        samplers, models, prompts = [], [], []
        for node in image_data['prompt'].values():
            if not might_be_sampler(node):
                continue

            inputs = node.get('inputs')
            if not inputs:
                continue

            sampler, model, prompt = self._get_sampler_data(image_data, inputs)
            samplers.append(sampler)
            if model:
                models.append(model)
            if prompt:
                prompts.append(prompt)

        return {
            'samplers': samplers,
            'models': models,
            'prompts': prompts,
            'metadata': {}
        }

    def _get_sampler_data(self, image_data: dict, inputs: dict):
        # sampler
        sampler_params = ((key, value) for key, value in inputs.items()
                          if key not in _SAMPLER_EXCLUDES)
        sampler = Sampler(
            name=inputs.get('sampler_name'),
            parameters=self._process_metadata(sampler_params))

        # model
        try:
            model_node = image_data['prompt'][inputs['model'][0]]
            model = Model(name=model_node['inputs']['ckpt_name'])
        except (KeyError, ValueError):
            model = None

        # prompt
        prompt = self._get_prompt(image_data, inputs)

        return sampler, model, prompt

    def _get_prompt(self, image_data: dict, inputs: dict):
        inputs_cache = image_data['inputs_cache']

        def get_prompt(input, text_keys) -> Tuple[Optional[Any], Optional[Prompt]]:
            if not input:
                return None, None
            source_id = input[0]
            # get cached prompt
            prompt = inputs_cache.get(source_id)
            if prompt:
                return source_id, prompt
            # collect reachable prompt parts
            parts = list(self._get_parts(image_data, source_id, text_keys))
            if not parts:
                return None, None
            # assemble prompt
            prompt = Prompt(value=",\n".join(parts), parts=parts)
            inputs_cache[source_id] = prompt
            return source_id, prompt

        positive_id, positive_prompt = get_prompt(
            inputs.get("positive"), self.text_positive_keys)
        negative_id, negative_prompt = get_prompt(
            inputs.get("negative"), self.text_negative_keys)

        if positive_id is None and negative_id is None:
            return None

        if (positive_id, negative_id) not in inputs_cache['uniq']:
            inputs_cache['uniq'].add((positive_id, negative_id))
            return positive_prompt, negative_prompt

        return None

    def _get_parts(self, image_data: dict, node_id, text_tags: Set[str], depth: int = 0
                   ) -> Iterable[str]:
        '''recursively search for all parts of a text prompt, starting from the given node id'''
        if self.traverse_limit != -1 and depth >= self.traverse_limit:
            return
        try:
            # test if the current node has prompt text
            node = image_data['prompt'][node_id]
            if not self.text_types or node['class_type'] in self.text_types:
                for text_key in text_tags & set(node['inputs'].keys()):
                    yield node['inputs'][text_key].strip()
        except KeyError:
            pass

        # explore other inputs fed into this node
        for output_id in image_data['links'].get(node_id, []):
            yield from self._get_parts(output_id, text_tags, depth + 1)
