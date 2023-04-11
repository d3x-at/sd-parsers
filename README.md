
## Features

Supports reading metadata from images generated with:
* Automatic1111's Stable Diffusion web UI
* ComfyUI
* Invoke AI

Provides a list of prompts used in the generation of the image, as well as generator-specific metadata.

## Usage
For a simple query, import ```ParserManager``` from ```sdparsers``` and use its ```parse()``` method to parse an image. (see [Examples](#Examples))

The ```ParserManager()``` constructor takes two arguments:
* config_file: If you want to provide alternate processing instructions. (absolute path to config file)
* process_items: If ```ParserManager``` should attempt to normalize the top-level keys in the ```metadata``` property. (defaults to ```True```)

### Output
The ```parse()``` method returns a ```PromptInfo``` type with the following properties (or ```None``` if no metadata was found):
* ```generator```: A simple string, specifying the parsing module that was used.

  ("AUTOMATIC1111" | "AUTOMATICStealth" | "ComfyUI" | "InvokeAI")

* ```prompts```: A list of prompts as found in the parsed metadata.

  In the form of ```(prompt, negative_prompt, weight)```.

  Weight is currently only parsed from InvokeAI metadata. As such, it's presence should not be relied on. (may be moved inside the Prompt type in the future)

* `samplers`: An unordered list of found samplers (and parameters)

* `models`: An unordered list of models used in the generation process

* ```metadata```: A dictionary of metadata besides the prompt information.

  Contains additional parameters which are found in the image metadata.

  Highly dependent on the provided data structure of the respective image generator.

  The key values of this dictionary will be normalized to be more consistent across image generators if ```ParserManager``` is used with ```process_items``` set to ```True``` (the default).
 
* ```raw_params```: A dictionary of the unmodified metadata entries found in the parsed image (if present).

  * Automatic1111: ```"parameters"```
  * InvokeAI: ```"sd-metadata"``` and ```"Dream"```
  * ComfyUI: ```"prompt"``` and ```"workflow"```


## Examples

Read prompt information from a given filename:
```python
from sdparsers import ParserManager

parser_manager = ParserManager()
prompt_data = parser_manager.parse('image.png')

for prompt in prompt_data.prompts:
    print("Prompt: {}\nNegative Prompt: {}".format(*prompt))
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

Directly using a specific parser, the configuration file is not read automatically. (see ```ParserManager.__init__()```)

Also, when not called via ```ParserManager```, the ```parse()``` method now requires a Pillow Image object as argument. (see ```ParserManager.parse()```)

## Credits
Prompt parsing logic adapted from AUTOMATIC1111's stable diffusion webui - https://github.com/AUTOMATIC1111/stable-diffusion-webui

Stealth PNGInfo code adopted from ashen-sensored's sd webui extension - https://github.com/ashen-sensored/sd_webui_stealth_pnginfo