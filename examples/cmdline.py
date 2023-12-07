"""
Display all metadata provided by sdparsers.
usage: python3 cmdline.py image.png
"""
import logging
import sys

from sd_parsers import ParserManager, PromptInfo


def main(files):
    parser_manager = ParserManager()
    for filename in files:
        try:
            prompt_info = parser_manager.parse(filename)
            if prompt_info:
                display_info(prompt_info)
        except Exception:
            logging.exception("error reading file: %s", filename)


def display_info(prompt_info: PromptInfo):
    # Models
    print(f"{len(prompt_info.models)} Model(s) used:")
    for model in prompt_info.models:
        print(f"Model: {model.name}\nModel Hash: {model.model_hash}")

    # Samplers
    print(f"\n{len(prompt_info.samplers)} Sampler(s) used:")
    for sampler in prompt_info.samplers:
        sampler_parameters = ", ".join(f"{k}: {v}" for k, v in sampler.parameters.items())
        print(f"Sampler: {sampler.name}\nSampler Parameters: {sampler_parameters}")

    # Prompts
    print(f"\n{len(prompt_info.prompts)} Prompt(s):")
    for prompt in prompt_info.prompts:
        print(f"Prompt: {prompt.value}")

    # Negative Prompts
    print(f"\n{len(prompt_info.negative_prompts)} Negative Prompt(s):")
    for prompt in prompt_info.negative_prompts:
        print(f"Negative Prompt: {prompt.value}")

    # Remaining metadata
    print("\nOther Metadata:")
    for k, v in prompt_info.metadata.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main(sys.argv[1:])
