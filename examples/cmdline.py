"""
Display all metadata provided by sdparsers.
usage: python3 cmdline.py image.png
"""
import logging
import sys

from sd_parsers import ParserManager
from sd_parsers.data import PromptInfo

parser_manager = ParserManager()


def main(files):
    for filename in files:
        try:
            prompt_info = parser_manager.parse(filename)
            if prompt_info:
                display_info(prompt_info)
        except Exception:
            logging.exception("error reading file: %s", filename)


def display_info(prompt_info: PromptInfo):
    # Models
    for model in prompt_info.models:
        print(f"Model: {model.name}\nModel Hash: {model.hash}")

    # Samplers
    for sampler in prompt_info.samplers:
        sampler_parameters = ", ".join(f"{k}: {v}" for k, v in sampler.parameters.items())
        print(f"Sampler: {sampler.name}\nSampler Parameters: {sampler_parameters}")

    # Combined Prompt
    print(f"\nPrompt: {prompt_info.full_prompt}")

    # Combined Negative Prompt
    print(f"\nNegative Prompt: {prompt_info.full_negative_prompt}")

    # Remaining metadata
    print("\nOther Metadata:")
    for k, v in prompt_info.metadata.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main(sys.argv[1:])
