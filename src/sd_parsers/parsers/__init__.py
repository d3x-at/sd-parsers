"""
Specialized parser classes for different image generators.

Metadata keys used as "trigger" for the different parsers are:
    * "parameters" or .jpeg -> automatic1111
    * "prompt" & "workflow" -> comfyui
    * "invokeai_metadata" or "sd-metadata" or "Dream" -> invokeai
    * "Description" & "Software" & "Source" & "Comment" -> novelai
"""
from ._automatic1111 import AUTOMATIC1111Parser
from ._comfyui import ComfyUIParser
from ._invokeai import InvokeAIParser
from ._novelai import NovelAIParser

MANAGED_PARSERS = [ComfyUIParser, InvokeAIParser, NovelAIParser, AUTOMATIC1111Parser]

__all__ = [
    "AUTOMATIC1111Parser",
    "InvokeAIParser",
    "NovelAIParser",
    "ComfyUIParser",
]
