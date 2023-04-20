from typing import Tuple

from ..parser import Parser, get_exif_value
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

SAMPLER_PARAMS_DEFAULT = ['CFG scale', 'Seed', 'Steps', 'ENSD']


class AUTOMATIC1111Parser(Parser):
    '''parse images created in AUTOMATIC1111's webui'''
    GENERATOR_ID = "AUTOMATIC1111"

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)
        self.sampler_params = self.config.get("sampler_params", SAMPLER_PARAMS_DEFAULT)

    @staticmethod
    def _get_parameters(image):
        if image.format == "PNG":
            return image.text.get('parameters')
        elif image.format in ("JPEG", "WEBP"):
            return get_exif_value(image, 'UserComment')
        return None

    def parse(self, image):
        parameters = self._get_parameters(image)
        if parameters is None:
            return None

        metadata = self._prepare_metadata(parameters)
        if metadata is None:
            return None

        return PromptInfo(self.GENERATOR_ID, *metadata, {"parameters": parameters})

    def _prepare_metadata(self, parameters: str):
        try:
            prompt, negative_prompt, metadata = split_parameters(parameters)
        except ValueError:
            return None

        prompts = [(
            Prompt(prompt, parts=[prompt]) if prompt else None,
            Prompt(negative_prompt, parts=[negative_prompt]) if negative_prompt else None
        )]

        models = []
        if 'Model' in metadata or 'Model hash' in metadata:
            model = Model(
                name=metadata.pop('Model', None),
                model_hash=metadata.pop('Model hash', None)
            )
            models.append(model)

        samplers = []
        if 'Sampler' in metadata:
            sampler_params = ((key, metadata.pop(key))
                              for key in list(metadata.keys())
                              if key in self.sampler_params)

            sampler = Sampler(
                name=metadata.pop('Sampler'),
                parameters=self._process_metadata(sampler_params)
            )
            samplers.append(sampler)

        return prompts, samplers, models, self._process_metadata(metadata)


def split_parameters(parameters: str) -> Tuple[str, str, dict]:
    '''
    split an A1111 parameters string into prompt, negative prompt and metadata
    :exception ValueError: If the metadata does not conform to the expected format.
    '''

    def split_meta(item: str) -> Tuple[str, str]:
        '''
        split metadata item into key:value pair
        :exception ValueError: If the item has more or less than two components.
        '''
        components = item.split(':')
        if len(components) != 2:
            raise ValueError("metadata malformed")
        key, value = map(str.strip, components)
        return key, value

    lines = parameters.split('\n')
    metadata = dict(split_meta(item) for item in lines[-1].split(','))

    if len(metadata) < 3:
        # actually a bit stricter than in the webui itself
        # grants some protection against "non-a1111" parameters
        raise ValueError("metadata too short")

    prompt_lines = lines[:-1]

    # prompt
    prompt = []
    i = 0
    for line in prompt_lines:
        line = line.strip()
        if line.startswith("Negative prompt:"):
            prompt_lines[i] = line[16:]
            break
        prompt.append(line)
        i += 1

    # negative prompt
    negative_prompt = [line.strip() for line in prompt_lines[i:]]

    return (
        "\n".join(prompt),
        "\n".join(negative_prompt),
        metadata
    )
