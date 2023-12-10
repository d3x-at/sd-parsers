import pytest
from sd_parsers import Prompt, Sampler

PROMPTS = [
    Prompt(
        value=(
            "professional full body photo of young woman, "
            "hyper long brunette hair, elegant hair, "
            "wearing a bikini top and asymmetric short skirt, "
            "curvy body, long legs, (imperfect skin), detailed skin, "
            "intense freckles, super long eye lashes, at night, outside, "
            "city background, 8k ultra detailed, realistic, high quality, "
            "film grain, low contrast"
        )
    )
]

NEGATIVE_PROMPTS = [Prompt(value="rendering, glowing eyes, skinny")]

PARAM = pytest.param(
    "invokeai_dream1.png",
    (
        Sampler(
            name="k_lms",
            parameters={
                "steps": 50,
                "cfg_scale": 5.0,
                "seed": 2980747362,
            },
            prompts=PROMPTS,
            negative_prompts=NEGATIVE_PROMPTS,
        ),
        set(),
        set(PROMPTS),
        set(NEGATIVE_PROMPTS),
        {
            "G": "0.9",
            "U": "4",
            "cf": "0.75",
            "height": 768,
            "width": 512,
            "size": "512x768",
        },
    ),
    id="invokeai_dream1.png",
)
