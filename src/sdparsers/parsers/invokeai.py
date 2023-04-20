import json
import re

from ..parser import Parser
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

SAMPLER_PARAMS_DEFAULT = ['cfg_scale', 'perlin', 'seed', 'steps', 'threshold']

_RE_PROMPT_NEGATIVES = re.compile(r'\[([^\[]*)\]')


class InvokeAIParser(Parser):
    GENERATOR_ID = "InvokeAI"

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)
        self.sampler_params = self.config.get("sampler_params", SAMPLER_PARAMS_DEFAULT)

    def parse(self, image):
        if image.format != "PNG":
            return None

        params_metadata = image.text.get('sd-metadata')
        if not params_metadata:
            return None

        raw_params = {'sd-metadata': params_metadata}
        params_dream = image.text.get('Dream')
        if params_dream:
            raw_params['Dream'] = params_dream

        try:
            prompts, sampler, model, metadata = self._prepare_metadata(params_metadata)
        except KeyError:
            return None

        return PromptInfo(self.GENERATOR_ID, prompts, sampler, model, metadata, raw_params)

    def _prepare_metadata(self, params_metadata):
        metadata = json.loads(params_metadata)

        def split_prompt(prompt: str, weight: float):
            negatives = list(map(str.strip, _RE_PROMPT_NEGATIVES.findall(prompt)))
            positive = _RE_PROMPT_NEGATIVES.sub('', prompt).strip()
            return (
                Prompt(
                    value=positive,
                    parts=[positive],
                    weight=weight) if positive else None,
                Prompt(
                    value=', '.join(negatives),
                    parts=negatives,
                    weight=weight) if negatives else None
            )

        metadata_image = dict(metadata.pop('image'))
        prompts = [split_prompt(prompt["prompt"], float(prompt["weight"]))
                   for prompt in metadata_image.pop('prompt')]

        sampler_params = ((key, metadata_image.pop(key))
                          for key in list(metadata_image.keys())
                          if key in self.sampler_params)

        sampler = Sampler(
            name=metadata_image.pop('sampler'),
            parameters=self._process_metadata(sampler_params)
        )

        model = Model(
            name=metadata.pop('model_weights'),
            model_hash=metadata.pop('model_hash', None)
        )

        return prompts, [sampler], [model], self._process_metadata({
            **metadata,
            **metadata_image
        })
