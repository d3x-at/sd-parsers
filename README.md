## Examples

Read prompt information from a given filename:
```python
from sdparsers import ParserManager

parser_manager = ParserManager()
prompt_data = parser_manager.parse('image.png')

print(prompt_data)
```

Read prompt information from an already opened image:
```python
from PIL import Image
from sdparsers import ParserManager

parser_manager = ParserManager()
with Image.open('image.png') as image:
    prompt_data = parser_manager.parse(image)

print(prompt_data)
```