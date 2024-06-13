"""
A library to read metadata from images created with Stable Diffusion.

Find more information at: https://github.com/d3x-at/sd-parsers

Basic usage:
-------------

.. highlight:: python
.. code-block:: python
from sd_parsers import ParserManager

parser_manager = ParserManager()

def main():
    prompt_info = parser_manager.parse("image.png")
    if prompt_info:
        print(prompt_info)
"""
from ._parser_manager import ParserManager

__all__ = ["ParserManager"]
