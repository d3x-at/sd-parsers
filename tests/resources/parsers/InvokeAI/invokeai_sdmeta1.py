import pytest
from sd_parsers.data import Model, Prompt, Sampler

PARAM = pytest.param(
    "invokeai_sdmeta1.png",
    (
        Sampler(
            name="k_lms",
            parameters={
                "steps": 50,
                "cfg_scale": 5,
                "threshold": 0,
                "perlin": 0,
                "seed": 2980747362,
            },
            model=Model(
                name="deliberateForInvoke_v08",
                hash="56d1442a0feefd64836a19ac8e3527ec71c884fc962e246ddf67b03e42921272",
            ),
            prompts=[
                Prompt(
                    1,
                    (
                        "professional full body photo of young woman, "
                        "hyper long brunette hair, elegant hair, "
                        "wearing a bikini top and asymmetric short skirt, "
                        "curvy body, long legs, (imperfect skin), detailed skin, "
                        "intense freckles, super long eye lashes, at night, outside, "
                        "city background, 8k ultra detailed, realistic, high quality, "
                        "film grain, low contrast"
                    ),
                    metadata={"weight": 1.0},
                )
            ],
            negative_prompts=[
                Prompt(
                    1,
                    "rendering, glowing eyes, skinny",
                    metadata={"weight": 1.0},
                )
            ],
        ),
        {
            "model": "stable diffusion",
            "app_id": "invoke-ai/InvokeAI",
            "app_version": "2.3.0",
            "height": 768,
            "width": 512,
            "seamless": False,
            "hires_fix": False,
            "type": "txt2img",
            "postprocessing": [
                {"type": "codeformer", "strength": 0.9, "fidelity": 0.75},
                {"type": "esrgan", "scale": 4, "strength": 0.95},
            ],
            "variations": [],
        },
    ),
    id="invokeai_sdmeta1.png",
)
