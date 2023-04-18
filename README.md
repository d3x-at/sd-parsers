
## Features

Supports reading metadata from images generated with:
* Automatic1111's Stable Diffusion web UI
* ComfyUI
* Invoke AI
* NovelAI

Provides a list of prompts used in the generation of the image, as well as generator-specific metadata.

## Installation
```
pip install sd-parsers
```

## Usage
For a simple query, import ```ParserManager``` from ```sdparsers``` and use its ```parse()``` method to parse an image. (see [examples](https://github.com/d3x-at/sd-parsers/tree/master/examples))

The ```ParserManager()``` constructor takes two arguments:
* `config_file`: If you want to provide alternate processing instructions. (absolute path to config file)
* `process_items`: If the parser should try to normalize the output across the different image sources. (defaults to `True`)

### Basic usage:

Read prompt information from a given filename:
```python
from sdparsers import ParserManager

parser_manager = ParserManager()
prompt_data = parser_manager.parse('image.png')

for prompt, negative_prompt in prompt_data.prompts:
    if prompt:
        print(f"Prompt: {prompt.value}")
    if negative_prompt:
        print(f"Negative Prompt: {negative_prompt.value}")
```

Read prompt information from an already opened image:
```python
from PIL import Image
from sdparsers import ParserManager

parser_manager = ParserManager()
with Image.open('image.png') as image:
    prompt_data = parser_manager.parse(image)

...
```

Each parser can also be used directly, omitting the use of ```ParserManager```.

For that simply import the specific parser instead:
```python
from PIL import Image
from sdparsers import AUTOMATIC1111Parser

parser = AUTOMATIC1111Parser()
with Image.open("image.png") as image:
    prompt_info = parser.parse(image)
```

Directly using a specific parser, the configuration file is not read automatically. (see `ParserManager.__init__()`)

Also, when not called via `ParserManager`, the `parse()` method now requires a Pillow Image object as argument. (see `ParserManager.parse()`)


### Output
The `parse()` method returns a `PromptInfo` type with the following properties (or `None` if no metadata was found):
* `generator`: A simple string, specifying the parsing module that was used.

  ("AUTOMATIC1111" | "AUTOMATICStealth" | "ComfyUI" | "InvokeAI")

* `prompts`: A list of tuples of prompts as found in the parsed metadata.

  In the form of `(prompt, negative_prompt)`.

* `samplers`: An unordered list of found samplers (and parameters).

  The key values of the parameters dictionary will be normalized to be more consistent across image generators if `ParserManager` is used with `process_items` set to `True`.

* `models`: An unordered list of models used in the generation process.

* `metadata`: A dictionary of metadata besides the prompt information.

  Contains additional parameters which are found in the image metadata.

  Highly dependent on the provided data structure of the respective image generator.

  The key values of this dictionary will be normalized to be more consistent across image generators if ```ParserManager``` is used with ```process_items``` set to ```True```.
 
* ```raw_params```: A dictionary of the unmodified metadata entries found in the parsed image (if present).

  * Automatic1111: ```"parameters"```
  * InvokeAI: ```"sd-metadata"``` and ```"Dream"```
  * ComfyUI: ```"prompt"``` and ```"workflow"```


## Credits
Idea and motivation using AUTOMATIC1111's stable diffusion webui
- https://github.com/AUTOMATIC1111/stable-diffusion-webui

Stealth PNGInfo code adopted from ashen-sensored's sd webui extension
- https://github.com/ashen-sensored/sd_webui_stealth_pnginfo

Example workflows for testing the ComfyUI parser
- https://github.com/comfyanonymous/ComfyUI_examples