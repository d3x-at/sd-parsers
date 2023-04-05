from typing import Dict, List, Tuple, NamedTuple, Optional, Any

class Prompt(NamedTuple):
    '''Represents an image generation prompt.'''
    value: str
    '''The value of the prompt.'''

class PromptInfo(NamedTuple):
    '''Holds prompt information.'''
    generator: str
    '''Name of the parser module which provided this information.'''
    prompts: List[Tuple[Prompt, Prompt, Optional[float]]]
    '''List of found generation prompts as tuples of (Prompt, Negative Prompt, Weight).'''
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
