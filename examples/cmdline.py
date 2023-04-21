"""
Display all metadata provided by sdparsers.
usage: python3 cmdline.py image.png
"""
import logging
import sys
import sdparsers as parser


def main(files):
    parser_manager = parser.ParserManager()
    for filename in files:
        try:
            prompt_info = parser_manager.parse(filename)
            if prompt_info:
                display_info(prompt_info)
        except Exception:
            logging.exception("error reading file: %s", filename)


def display_info(prompt_info: parser.PromptInfo):
    # Models
    print(f"{len(prompt_info.models)} Model(s) used:")
    for model in prompt_info.models:
        print(f"Model: {model.name}\nModel Hash: {model.model_hash}")

    # Samplers
    print(f"\n{len(prompt_info.samplers)} Sampler(s) used:")
    for sampler in prompt_info.samplers:
        sampler_parameters = ", ".join(
            f"{k}: {v}" for k, v in sampler.parameters.items())
        print(f"Sampler: {sampler.name}\nSampler Parameters: {sampler_parameters}")

    # Prompts
    print(f"\n{len(prompt_info.prompts)} Prompt(s):")
    for prompt, negative_prompt in prompt_info.prompts:
        if prompt:
            print(f"Prompt: {prompt.value}")
        if negative_prompt:
            print(f"Negative Prompt: {negative_prompt.value}")

    # Remaining metadata
    print("\nOther Metadata:")
    for k, v in prompt_info.metadata.items():
        print(f"{k}: {v}")

    # Some (not all) raw parameters
    if prompt_info.generator == parser.AUTOMATIC1111Parser.GENERATOR_ID:
        print(f"\nRaw Parameters: {prompt_info.raw_params.get('parameters')}")

    elif prompt_info.generator == parser.InvokeAIParser.GENERATOR_ID:
        print(f"\nRaw Parameters: {prompt_info.raw_params.get('sd-metadata')}")

    elif prompt_info.generator == parser.ComfyUIParser.GENERATOR_ID:
        print(f"\nRaw Parameters: {prompt_info.raw_params.get('prompt')}")

    elif prompt_info.generator == parser.NovelAIParser.GENERATOR_ID:
        print(f"\nRaw Parameters: {prompt_info.raw_params.get('Comment')}")

if __name__ == "__main__":
    main(sys.argv[1:])
