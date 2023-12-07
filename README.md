
## Features

Supports reading metadata from images generated with:
* Automatic1111's Stable Diffusion web UI
* ComfyUI *
* InvokeAI
* NovelAI

Provides a list of prompts used in the generation of the image, as well as generator-specific metadata.

\* Custom ComfyUI nodes might parse incorrectly / with incomplete data.

## Installation
```
pip install sd-parsers
```

## Usage
For a simple query, import ```ParserManager``` from ```sd_parsers``` and use its ```parse()``` method to parse an image. (see [examples](examples))

### Basic usage:

Read prompt information from a given filename:
```python
from sd_parsers import ParserManager

parser_manager = ParserManager()
prompt_info = parser_manager.parse("image.png")

if prompt_info:
    for prompt in prompt_info.prompts:
        print(f"Prompt: {prompt.value}")
```

Read prompt information from an already opened image:
```python
from PIL import Image
from sd_parsers import ParserManager

parser_manager = ParserManager()
with Image.open('image.png') as image:
    prompt_info = parser_manager.parse(image)
```

Each parser module can also be used directly, omitting the use of ```ParserManager```:

```python
from PIL import Image
from sd_parsers import ParserError
from sd_parsers.parsers import AUTOMATIC1111Parser

parser = AUTOMATIC1111Parser()
with Image.open("image.png") as image:
    prompt_info, error = parser.read_parameters(image)
    
    if prompt_info:
        # the following can be omitted for an equivalent
        # of ParserManager(lazy_read=True)
        try:
            prompt_info.parse()
        except ParserError:
            ...
```

### Output
The output returned from `ParserManager` is a `PromptInfo` type with the following properties (or `None` if no metadata was found):
* `generator`: Specifies the image generator that may have been used for creating the image.

* `prompts`: Prompts as found in the parsed metadata.

* `negative_prompts`: Negative prompts as found in the parsed metadata.

* `samplers`: Samplers used in the image generation process.

* `models`: Models used in the image generation process.

* `metadata`: Additional metadata which could not be attributed to one of the former described.

  Highly dependent on the provided data structure of the respective image generator.

* ```parameters```: A dictionary of unmodified metadata entries as found in the parsed image (if present).


## Credits
Idea and motivation using AUTOMATIC1111's stable diffusion webui
- https://github.com/AUTOMATIC1111/stable-diffusion-webui

Example workflows for testing the ComfyUI parser
- https://github.com/comfyanonymous/ComfyUI_examples