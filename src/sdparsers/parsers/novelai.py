import json
import re

from ..parser import Parser
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

SAMPLER_PARAMS_DEFAULT = ["seed", "strength", "noise", "scale"]


class NovelAIParser(Parser):
    GENERATOR_ID = "NovelAI"

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)
        self._re_model = re.compile(r'^(.*?)\s+([A-Z0-9]+)$')
        self.sampler_params = self.config.get("sampler_params", SAMPLER_PARAMS_DEFAULT)

    def parse(self, image):
        if image.format != "PNG":
            return None

        params_comment = image.text.get('Comment')
        params_description = image.text.get('Description')
        params_software = image.text.get('Software')
        params_source = image.text.get('Source')

        if params_software != "NovelAI" \
                or params_comment is None \
                or params_description is None \
                or params_source is None:
            return None

        metadata = self._prepare_metadata(
            params_comment, params_description, params_source)

        return PromptInfo(generator=self.GENERATOR_ID, **metadata,
                          raw_params={
                              'Comment': params_comment,
                              'Description': params_description,
                              'Software': params_software,
                              'Source': params_source
                          })

    def _prepare_metadata(self, params_comment, params_description, params_source):
        metadata = json.loads(params_comment)

        # prompt
        positive_prompt = params_description.strip()
        negative_prompt = metadata.pop("uc", None)
        prompt = (
            Prompt(positive_prompt, parts=[positive_prompt]),
            Prompt(negative_prompt, parts=[negative_prompt])
            if negative_prompt else None
        )

        # model
        models = []
        match = self._re_model.fullmatch(params_source)
        if match:
            model_name, model_hash = match.groups()
            model = Model(model_name, model_hash)
            models.append(model)

        # sampler
        sampler_parameters = []
        for key in self.sampler_params:
            param = metadata.pop(key, None)
            if param:
                sampler_parameters.append((key, param))

        samplers = []
        try:
            sampler = Sampler(name=metadata.pop("sampler"),
                              parameters=self._process_metadata(sampler_parameters))
            samplers.append(sampler)
        except KeyError:
            pass

        return {
            "prompts": [prompt],
            "samplers": samplers,
            "models": models,
            "metadata": self._process_metadata(metadata)
        }
