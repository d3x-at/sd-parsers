from typing import Dict, List, Tuple, NamedTuple, Optional, Any


class Prompt(NamedTuple):
    '''Represents an image generation prompt.'''
    value: str
    '''The value of the prompt.'''
    parts: Optional[List[str]] = None
    '''Contains all parts making up a prompt. (Specific to ComfyUI parser for now)'''
    weight: Optional[float] = None
    '''Prompt weight. (Specific to InvokeAI for now)'''


class Sampler(NamedTuple):
    name: str
    parameters: Dict[str, Any]


class Model(NamedTuple):
    name: Optional[str] = None
    model_hash: Optional[str] = None


class PromptInfo(NamedTuple):
    '''Holds prompt information.'''
    generator: str
    '''Name of the parser module which provided this information.'''
    prompts: List[Tuple[Optional[Prompt], Optional[Prompt]]]
    '''List of found generation prompts as tuples of (Prompt, Negative Prompt).'''
    samplers: List[Sampler]
    '''Unordered list of used samplers'''
    models: List[Model]
    '''Unordered list of used models'''
    metadata: Dict[str, Any]
    '''
    Contains additional parameters which are found in the image metadata.

    Highly dependent on the provided data structure of the respective image generator.

    The key values of this dictionary will be normalized to be more consistent
    across image generators if ParserManager is used with
    "process_items" set to "True" (the default).
    '''
    raw_params: Dict[str, str]
    '''The original parameters as found in the image metadata.'''
