import json
from ..parser import Parser
from ..prompt_info import Prompt, PromptInfo, Sampler

SAMPLER_PARAMS_DEFAULT = ["seed", "strength", "noise", "scale"]


class NovelAIParser(Parser):
    GENERATOR_ID = "NovelAI"

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)
        self.sampler_params = self.config.get("sampler_params", SAMPLER_PARAMS_DEFAULT)

    def parse(self, image):
        params_comment = image.info.get('Comment')
        params_description = image.info.get('Description')

        if params_comment is None or params_description is None:
            return None

        metadata = self._prepare_metadata(params_comment, params_description)
        if metadata is None:
            return None

        return PromptInfo(generator=self.GENERATOR_ID, **metadata,
                          raw_params={
                              'Comment': params_comment,
                              'Description': params_description
                          })

    def _prepare_metadata(self, params_comment, params_description):
        metadata = json.loads(params_comment)

        # prompt
        negative_prompt_value = metadata.pop("uc", None)
        prompt = (
            Prompt(params_description.strip()),
            Prompt(negative_prompt_value) if negative_prompt_value else None
        )

        # sampler
        sampler_parameters = []
        for key in self.sampler_params:
            param = metadata.pop(key, None)
            if param:
                sampler_parameters.append((key, param))

        if not sampler_parameters:
            return None

        try:
            sampler = Sampler(name=metadata.pop("sampler"),
                              parameters=self._process_metadata(sampler_parameters))
        except KeyError:
            return None

        return {
            "prompts": [prompt],
            "samplers": [sampler],
            "models": [],
            "metadata": self._process_metadata(metadata)
        }
