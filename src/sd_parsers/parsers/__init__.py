"""Specialized parser classes for different image generators."""
from ._automatic1111 import AUTOMATIC1111Parser
from ._comfyui import ComfyUIParser
from ._invokeai import InvokeAIParser
from ._novelai import NovelAIParser

__all__ = [
    "AUTOMATIC1111Parser",
    "InvokeAIParser",
    "NovelAIParser",
    "ComfyUIParser",
]
