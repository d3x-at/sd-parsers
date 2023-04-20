import json
import typing
from collections import defaultdict

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

        prompts, samplers, models = self._prepare_metadata(params_prompt, params_workflow)

        return PromptInfo(self.GENERATOR_ID, prompts, samplers, models, {}, {
            "prompt": params_prompt,
            "workflow": params_workflow
        })

    def _prepare_metadata(self, params_prompt: str, params_workflow: str):
        prompt_data = json.loads(params_prompt)
        workflow_data = json.loads(params_workflow)

        links = defaultdict(list)
        try:
            for _, output_id, _, input_id, _, link_type in workflow_data["links"]:
                if link_type in self.traverse_types:
                    links[input_id].append(output_id)
        except ValueError:
            pass

        def get_prompts(node_id: int, text_tags: typing.Set[str], depth: int = 0) -> typing.Iterable[str]:
            '''recursively search for a text prompt, starting from the given node id'''
            if self.traverse_limit != -1 and depth >= self.traverse_limit:
                return
            try:
                # test if the current node has prompt text
                node = prompt_data[str(node_id)]
                if not self.text_types or node['class_type'] in self.text_types:
                    for text_key in text_tags & set(node['inputs'].keys()):
                        yield node['inputs'][text_key].strip()
            except KeyError:
                pass

            # explore other inputs fed into this node
            for output_id in links.get(node_id, []):
                yield from get_prompts(output_id, text_tags, depth + 1)

        # check all sampler types
        samplers = []
        models = []
        prompt_ids = []
        for sampler, positive_id, negative_id, model in self._get_samplers(prompt_data):
            samplers.append(sampler)
            if model:
                models.append(model)
            prompt_ids.append((positive_id, negative_id))

        # ignore multiple uses
        prompts = []
        for positive_id, negative_id in set(prompt_ids):
            positive_prompts = list(get_prompts(positive_id, self.text_positive_keys)) \
                if positive_id else None
            negative_prompts = list(get_prompts(negative_id, self.text_negative_keys)) \
                if negative_id else None

            if negative_prompts or positive_prompts:
                prompts.append((
                    Prompt(value=",\n".join(positive_prompts), parts=positive_prompts)
                    if positive_prompts else None,
                    Prompt(value=",\n".join(negative_prompts), parts=negative_prompts)
                    if negative_prompts else None
                ))

        return prompts, samplers, models

    def _get_samplers(self, prompt_data):
        def might_be_sampler(node):
            try:
                if self.sampler_types:
                    return node['class_type'] in self.sampler_types
                return all(key in node['inputs'].keys() for key in _SAMPLER_EXCLUDES)
            except KeyError:
                return False

        for node in prompt_data.values():
            if not might_be_sampler(node):
                continue

            inputs = node.get('inputs')
            if not inputs:
                continue

            sampler_params = ((key, value) for key, value in inputs.items()
                              if key not in _SAMPLER_EXCLUDES)

            sampler = Sampler(
                name=inputs.get('sampler_name'),
                parameters=self._process_metadata(sampler_params))

            positive_input = inputs.get("positive")
            positive_id = int(positive_input[0]) if positive_input else None

            negative_input = inputs.get("negative")
            negative_id = int(negative_input[0]) if negative_input else None

            try:
                model_node = prompt_data[inputs['model'][0]]
                model = Model(name=model_node['inputs']['ckpt_name'])
            except (KeyError, ValueError):
                model = None

            yield sampler, positive_id, negative_id, model
