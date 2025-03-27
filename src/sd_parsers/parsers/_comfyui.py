"""Parser for images generated by ComfyUI or similar."""

import json
import logging
from collections import defaultdict
from contextlib import suppress
from typing import Any, Dict, Generator, List, Optional, Set, Tuple


from sd_parsers.data import Generators, Model, Prompt, Sampler, PromptInfo
from sd_parsers.exceptions import ParserError

from ._parser import Parser, ReplacementRules

logger = logging.getLogger(__name__)

SAMPLER_TYPES = ["WanVideoSampler"]
SAMPLER_PARAMS = {"sampler_name", "steps", "cfg"}

REPLACEMENT_RULES: ReplacementRules = [("cfg", "cfg_scale")]

POSITIVE_PROMPT_KEYS = ["text", "positive"]
NEGATIVE_PROMPT_KEYS = ["text", "negative"]
IGNORE_LINK_TYPES_PROMPT = ["CLIP"]
IGNORE_CLASS_TYPES = ["ConditioningCombine"]


class ComfyUIParser(Parser):
    """Parser for images generated by ComfyUI"""

    generator = Generators.COMFYUI

    def parse(self, parameters: Dict[str, Any]) -> PromptInfo:
        try:
            prompt = parameters["prompt"]
            if not isinstance(prompt, dict):
                prompt = json.loads(prompt)

            workflow = parameters["workflow"]
            if not isinstance(workflow, dict):
                workflow = json.loads(workflow)
        except Exception as error:
            raise ParserError("error reading parameters") from error

        samplers, metadata = _ImageContext.extract(self, prompt, workflow)

        return PromptInfo(self.generator, samplers, metadata, parameters)


class _ImageContext:
    parser: ComfyUIParser
    prompt: Dict[str, Dict[str, Any]]
    links: Dict[str, Dict[str, Set[str]]]
    processed_nodes: Set[str]

    @property
    def _debug(self):
        return self.parser._debug

    def __init__(self, parser: ComfyUIParser, prompt: Dict, workflow: Dict):
        self.parser = parser
        self.processed_nodes = set()

        # ensure that prompt keys are strings
        try:
            self.prompt = {str(k): v for k, v in prompt.items()}
        except (AttributeError, ValueError) as error:
            raise ParserError("prompt has unexpected format") from error

        # build links dictionary (dict[input_id, dict[output_id, set[link_type]]])
        self.links = defaultdict(lambda: defaultdict(set))
        try:
            for _, output_id, _, input_id, _, link_type in workflow["links"]:
                self.links[str(input_id)][str(output_id)].add(link_type)
        except (TypeError, KeyError, ValueError) as error:
            raise ParserError("workflow has unexpected format") from error

    @classmethod
    def extract(
        cls, parser: ComfyUIParser, prompt: Dict, workflow: Dict
    ) -> Tuple[List[Sampler], Dict[str, List[Dict[str, Any]]]]:
        """Extract samplers with their child parameters aswell as metadata"""
        context = cls(parser, prompt, workflow)
        samplers = []
        metadata = defaultdict(list)

        # Pass 1: get samplers and related data
        for node_id, node in context.prompt.items():
            sampler = context._try_get_sampler(node_id, node)
            if sampler:
                samplers.append(sampler)

        # Pass 2: put information from unprocessed nodes into metadata
        for node_id, node in context.prompt.items():
            if node_id in context.processed_nodes:
                continue

            with suppress(KeyError):
                inputs = context._get_input_values(node["inputs"], node_id)
                if inputs:
                    metadata[node["class_type"]].append(inputs)

        return samplers, dict(metadata)

    def _try_step_into(self, node_inputs: dict, node_names: List[str]):
        """
        see if one of the given inputs exists in the current node

        and return the first found node's inputs dictionary

        if none is found, return the original inputs
        """
        for name in node_names:
            try:
                target_id = node_inputs[name][0]
                target_node = self.prompt[target_id]
                inputs = dict(target_node["inputs"])
                return inputs
            except (TypeError, KeyError, ValueError):
                continue

        return node_inputs

    def _try_get_sampler(self, node_id: str, node: Dict[str, Any]):
        """Test if this node could contain sampler data"""
        try:
            inputs = dict(node["inputs"])
            if node["class_type"] not in SAMPLER_TYPES and not SAMPLER_PARAMS.issubset(
                inputs.keys()
            ):
                return None
        except (KeyError, TypeError):
            return None

        if self._debug:
            logger.debug("found sampler #%s", node_id)
        self.processed_nodes.add(node_id)

        # Sampler parameters
        sampler_name = next(
            (inputs.pop(key) for key in ["sampler_name", "scheduler"] if key in inputs), "unknown"
        )
        sampler_parameters = self.parser.normalize_parameters(
            self._get_input_values(inputs), REPLACEMENT_RULES
        )

        # Sampler
        sampler = {
            "sampler_id": node_id,
            "name": sampler_name,
            "parameters": sampler_parameters,
        }

        # Model
        with suppress(KeyError, ValueError):
            model_id = inputs["model"][0]
            sampler["model"] = self._get_model(model_id)

        # check for WanVideoSampler's TextEmbed node
        prompt_inputs = self._try_step_into(inputs, ["text_embeds"])

        # Prompt
        with suppress(KeyError, ValueError):
            positive_prompt_id = prompt_inputs["positive"][0]
            sampler["prompts"] = self._get_prompts(
                positive_prompt_id,
                POSITIVE_PROMPT_KEYS,
            )

        # Negative Prompt
        with suppress(KeyError, ValueError):
            negative_prompt_id = prompt_inputs["negative"][0]
            sampler["negative_prompts"] = self._get_prompts(
                negative_prompt_id,
                NEGATIVE_PROMPT_KEYS,
            )

        return Sampler(**sampler)

    def _get_model(self, initial_node_id: str) -> Optional[Model]:
        """Get the first model reached from the given node_id"""
        if self._debug:
            logger.debug("looking for model: #%s", initial_node_id)

        for node_id, node, trace in self._traverse(initial_node_id):
            try:
                inputs = dict(node["inputs"])
                ckpt_name = next(
                    (inputs.pop(key) for key in ["ckpt_name", "model"] if key in inputs)
                )
            except (KeyError, TypeError, StopIteration):
                pass
            else:
                self.processed_nodes.add(node_id)
                if self._debug:
                    logger.debug("found model #%s: %s", node_id, ckpt_name)

                metadata = self._get_input_values(inputs)
                metadata.update(self._get_trace_metadata(trace))

                model = Model(model_id=node_id, name=ckpt_name, metadata=metadata)
                return model

        return None

    def _get_prompts(self, initial_node_id: str, text_keys: List[str]) -> List[Prompt]:
        """Get all prompts reachable from a given node_id."""
        if self._debug:
            logger.debug("looking for prompts: %s", initial_node_id)

        prompts = []

        def check_inputs(node_id: str, inputs: Dict, trace: List[str]) -> bool:
            found_prompt = False
            for key in text_keys:
                try:
                    text = inputs.pop(key)
                except KeyError:
                    continue

                if isinstance(text, str):
                    if self._debug:
                        logger.debug("found prompt %s#%s: %s", key, node_id, text)

                    metadata = self._get_input_values(inputs)
                    metadata.update(self._get_trace_metadata(trace))

                    prompts.append(
                        Prompt(
                            value=text.strip(),
                            prompt_id=node_id,
                            metadata=metadata,
                        )
                    )
                    found_prompt = True

            if found_prompt:
                self.processed_nodes.update([node_id], trace)
                return False
            return True

        prompt_iterator = self._traverse(initial_node_id, IGNORE_LINK_TYPES_PROMPT)
        with suppress(StopIteration):
            node_id, node, trace = next(prompt_iterator)
            while True:
                recurse = True
                try:
                    inputs = node["inputs"]
                except KeyError:
                    pass
                else:
                    recurse = check_inputs(node_id, dict(inputs), trace)

                node_id, node, trace = prompt_iterator.send(recurse)

        return prompts

    def _traverse(
        self, node_id: str, ignored_link_types: Optional[List[str]] = None
    ) -> Generator[Tuple[str, Any, List[str]], Optional[bool], None]:
        """Traverse backwards through node tree, starting at a given node_id"""
        visited = set()
        ignore_links = set(ignored_link_types) if ignored_link_types else set()

        def traverse_inner(node_id: str, trace: List[str]):
            visited.add(node_id)

            with suppress(KeyError):
                recurse = yield node_id, self.prompt[node_id], trace[:-1]
                if recurse is False:
                    return

            with suppress(KeyError, RecursionError):
                for link_id, link_types in self.links[node_id].items():
                    if link_id not in visited and link_types - ignore_links:
                        if self._debug:
                            logger.debug(
                                "%s->%s, %s%s", node_id, link_id, "." * len(trace), link_types
                            )
                        yield from traverse_inner(link_id, trace + [link_id])

        yield from traverse_inner(node_id, [node_id])

    def _get_trace_metadata(self, trace: List[str]):
        metadata = {}

        for node_id in trace:
            try:
                node = self.prompt[node_id]
                class_type = node["class_type"]

                if class_type in IGNORE_CLASS_TYPES:
                    continue

                value = self._get_input_values(node["inputs"], node_id)

            except KeyError:
                continue

            try:
                entry = metadata[class_type]
                if isinstance(entry, list):
                    entry.append(value)
                else:
                    metadata[class_type] = [entry, value]
            except KeyError:
                metadata[class_type] = value

        return metadata

    def _get_input_values(
        self,
        inputs: Dict[str, Any],
        node_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        with suppress(Exception):
            vals = {key: value for key, value in inputs.items() if not isinstance(value, list)}
            if vals:
                return vals if node_id is None else {"id": node_id, **vals}
        return {}
