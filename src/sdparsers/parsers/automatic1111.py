import json
import re
from typing import Optional, Tuple, Iterable

from ..parser import Parser, get_exif_value
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

SAMPLER_PARAMS_DEFAULT = ['CFG scale', 'Seed', 'Steps', 'ENSD']

_RE_CIVITAI_HASHES = re.compile(r'(?:,\s*)?Hashes:\s*(\{[^\}]*\})\s*')


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
    def split_meta(last_line: str) -> Iterable[Tuple[str, str]]:
        for item in last_line.split(','):
            try:
                key, value = map(str.strip, item.split(':'))
                yield key, value
            except ValueError:
                pass

    last_newline = parameters.rfind("\n")
    if last_newline == -1:
        raise ValueError("malformed parameters")

    last_line, hashes = get_civitai_hashes(parameters[last_newline:])
    metadata = dict(split_meta(last_line))
    if len(metadata) < 3:
        # actually a bit stricter than in the webui itself
        # grants some protection against "non-a1111" parameters
        raise ValueError("metadata too short")

    prompts = parameters[:last_newline].split('Negative prompt:')
    prompt, negative_prompt = prompts + ['']*(2-len(prompts))
    if hashes:
        metadata["hashes"] = hashes

    return (
        prompt.strip("\n "),
        negative_prompt.strip("\n "),
        metadata
    )


def get_civitai_hashes(line: str) -> Tuple[str, Optional[dict]]:
    hashes = None
    match = _RE_CIVITAI_HASHES.search(line)
    if match:
        hashes = json.loads(match.group(1))
        start, end = match.span(0)
        line = line[:start] + line[end:]
    return line, hashes
