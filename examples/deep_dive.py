"""
Display all metadata provided by sdparsers.
Works best on images generated with ComfyUI

usage: python3 deep_dive.py ../tests/resources/parsers/ComfyUI/night_evening_day_morning_cropped.png
"""
import logging
import sys

from sd_parsers import ParserManager
from sd_parsers.data import Sampler

parser_manager = ParserManager()


def main(files):
    for filename in files:
        try:
            prompt_info = parser_manager.parse(filename)
            if prompt_info:
                for i, sampler in enumerate(prompt_info.samplers):
                    show_sampler(i, sampler)

                print(f"\nRemaining Metadata: {prompt_info.metadata}")
        except Exception:
            logging.exception("error reading file: %s", filename)


def show_sampler(i: int, sampler: Sampler):
    print(f"\n{'#'*80}\nSampler #{i+1}: {sampler.name}\n{'#'*80}")

    if sampler.model:
        print(f"\nModel: {sampler.model}")

    if sampler.prompts:
        print("\nPrompts:")
        for prompt in sampler.prompts:
            print(f"Prompt: {prompt}\nMetadata: {prompt.metadata}")

    if sampler.negative_prompts:
        print("\nNegative Prompts:")
        for prompt in sampler.negative_prompts:
            print(f"Prompt: {prompt}\nMetadata: {prompt.metadata}")

    print(f"\nSampler Parameters: {sampler.parameters}")


if __name__ == "__main__":
    main(sys.argv[1:])
