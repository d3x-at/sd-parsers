import re

from ..parser import Parser, get_exif_value
from ..prompt_info import Model, Prompt, PromptInfo, Sampler

GENERATOR_ID = "AUTOMATIC1111"
SAMPLER_PARAMS_DEFAULT = ['CFG scale', 'Seed', 'Steps', 'ENSD']


class AUTOMATIC1111Parser(Parser):
    '''parse images created in AUTOMATIC1111's webui'''
    RE_PARAM = re.compile(
        r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)')

    def __init__(self, config=None, process_items=True):
        super().__init__(config, process_items)
        self.sampler_params = self.config.get("sampler_params", SAMPLER_PARAMS_DEFAULT)

    def parse(self, image):
        parameters = self._get_parameters(image)
        if parameters is None:
            return None

        prompt, model, sampler, metadata = self._prepare_metadata(parameters)
        if not metadata:
            return None

        return PromptInfo(GENERATOR_ID, [prompt], [sampler], [model], metadata,
                         {"parameters": parameters})

    @staticmethod
    def _get_parameters(image):
        if image.format == "PNG":
            return image.info.get('parameters')
        elif image.format in ("JPEG", "WEBP"):
            return get_exif_value(image, 'UserComment')
        return None

    def _prepare_metadata(self, parameters: str):

        def get_metadata(parameters):
            lines = parameters.split("\n")
            metadata = self.RE_PARAM.findall(lines[-1].strip())
            if len(metadata) < 3:
                return lines, None
            return lines[:-1], dict(metadata)

        lines, metadata = get_metadata(parameters)
        prompt, negative_prompt = [], []
        i = 0

        # prompt
        for line in lines:
            line = line.strip()
            if line.startswith("Negative prompt:"):
                lines[i] = line[16:]
                break
            prompt.append(line)
            i += 1

        # negative prompt
        for line in lines[i:]:
            negative_prompt.append(line.strip())

        prompt = (
            Prompt("\n".join(prompt)),
            Prompt("\n".join(negative_prompt)))

        model = Model(
            name=metadata.pop('Model', None),
            model_hash=metadata.pop('Model hash', None)
        )

        sampler = Sampler(
            name=metadata.pop('Sampler'),
            parameters=self._process_metadata(
                (key, value) for key, value in metadata.items()
                if key in self.sampler_params)
        )

        return prompt, model, sampler, self._process_metadata(
            (key, value) for key, value in metadata.items()
            if key not in self.sampler_params)
        