from typing import Dict, List, Tuple, NamedTuple, Any

class Prompt(NamedTuple):
    value: str

class PromptInfo(NamedTuple):
    '''holds prompt information'''
    generator: str
    prompts: List[Tuple[Prompt, Prompt]]
    processing_info: List[Tuple[str, str]]
    raw_params: Dict[str, Any]
