## Features

Supports reading metadata from images generated with:
* Automatic1111's Stable Diffusion web UI
* ComfyUI *
* Fooocus
* InvokeAI
* NovelAI

Provides a list of prompts used in the generation of the image, as well as generator-specific metadata.

\* Custom ComfyUI nodes might parse incorrectly / with incomplete data.

## Installation
```
pip install sd-parsers
```

## Usage

From command line: ```python3 -m sd_parsers <filenames>```.


### Basic usage:

For a simple query, import ```ParserManager``` from ```sd_parsers``` and use its ```parse()``` method to parse an image. (see [examples](examples))

#### Read prompt information from a given filename with `parse()`:
```python
from sd_parsers import ParserManager

parser_manager = ParserManager()

def main():
    prompt_info = parser_manager.parse("image.png")

    if prompt_info:
        for prompt in prompt_info.prompts:
            print(f"Prompt: {prompt.value}")
```

#### Read prompt information from an already opened image:
```python
from PIL import Image
from sd_parsers import ParserManager

parser_manager = ParserManager()

def main():
    with Image.open('image.png') as image:
        prompt_info = parser_manager.parse(image)
```

#### Each parser module can also be used directly, omitting the use of ```ParserManager```:

```python
from PIL import Image
from sd_parsers.data import PromptInfo
from sd_parsers.exceptions import ParserError
from sd_parsers.parsers import AUTOMATIC1111Parser

parser = AUTOMATIC1111Parser()


def main():
    try:
        with Image.open("image.png") as image:
            # read_parameters() returns relevant image metadata parameters
            # and optional context information needed for parsing
            parameters, parsing_context = parser.read_parameters(image)

        # parse() builds a standardized data structure from the raw parameters
        generator, samplers, metadata = parser.parse(parameters, parsing_context)

    except ParserError:
        ...

    # creating a PromptInfo object from the obtained data allows for the use
    # of convenience poperties like ".prompts" or ".models"
    prompt_info = PromptInfo(generator, samplers, metadata, parameters)
```

### Output
The `parse()` method returns a `PromptInfo` ([source](src/sd_parsers/data/prompt_info.py)) object when suitable metadata is found.

> Use ```python3 -m sd_parsers <image.png>``` to get an idea of the data parsed from an image file.

> To get a result in JSON form, an approach as demonstrated in https://github.com/d3x-at/sd-parsers-web can be used.

`PromptInfo` contains the following properties :
* `generator`: Specifies the image [generator](src/sd_parsers/data/generators.py) that may have been used for creating the image.

* `full_prompt`: A full prompt, if present in the image metadata.

  Otherwise, a simple concatenation of all prompts found.

* `full_negative_prompt`: A full negative prompt if present in the image metadata. 
  
  Otherwise, a simple concatenation of all negative prompts found.

* `prompts`: All [prompts](src/sd_parsers/data/prompt.py) found in the parsed metadata.

* `negative_prompts`: All negative [prompts](src/sd_parsers/data/prompt.py) found in the parsed metadata.

* `models`: [Models](src/sd_parsers/data/model.py) used in the image generation process.

* `samplers`: [Samplers](src/sd_parsers/data/sampler.py) used in the image generation process.

  A Sampler contains the following properties specific to itself:
    * `name`: The name of the sampler

    * `parameters`: Generation parameters, including _cfg_scale_, _seed_, _steps_ and others.

    * `sampler_id`: A unique id of the sampler (if present in the metadata)

    * `model`: The model used by this sampler.

    * `prompts`: A list of positive prompts used by this sampler.
    
    * `negative_prompts`: A list of negative prompts used by this sampler.

* `metadata`: Additional metadata which could not be attributed to one of the former described.

  Highly dependent on the provided data structure of the respective image generator.

* `raw_parameters`: The unprocessed metadata entries as found in the parsed image (if present).

## Contributing
As i don't have the time and resources to keep up with all the available AI-based image generators out there, the scale and features of this library is depending greatly on your help.

If you find the sd-parsers library unable to read metadata from an image, feel free to open an [issue](https://github.com/d3x-at/sd-parsers/issues).

See [CONTRIBUTING.md](https://github.com/d3x-at/sd-parsers/blob/master/.github/CONTRIBUTING.md), if you are willing to help with improving the library itself and/or to create/maintain an additional parser module.


## Credits
Idea and motivation using AUTOMATIC1111's stable diffusion webui
- https://github.com/AUTOMATIC1111/stable-diffusion-webui

Example workflows for testing the ComfyUI parser
- https://github.com/comfyanonymous/ComfyUI_examples
