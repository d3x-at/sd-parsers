import pytest
from sd_parsers import Model, Prompt, Sampler

MODEL = Model(
    name="v1-5-pruned-emaonly.ckpt", parameters={"config_name": "v1-inference.yaml"}, model_id=4
)

PROMPTS = [
    Prompt(
        value="photograph of victorian woman with wings, sky clouds, " "meadow grass",
        prompt_id=6,
    )
]

NEGATIVE_PROMPTS = [Prompt(value="watermark, text", prompt_id=7)]

PARAM = pytest.param(
    "img2img_cropped.png",
    (
        [
            Sampler(
                name="sample_dpmpp_2m",
                parameters={
                    "seed": 280823642470253,
                    "random_seed_after_every_gen": True,
                    "steps": 20,
                    "cfg": 8.0,
                    "scheduler": "normal",
                    "denoise": 0.8700000000000001,
                },
                sampler_id=3,
                model=MODEL,
                prompts=PROMPTS,
                negative_prompts=NEGATIVE_PROMPTS,
            ),
        ],
        set([MODEL]),
        set(PROMPTS),
        set(NEGATIVE_PROMPTS),
        {
            ("SaveImage", 9): {"filename_prefix": "ComfyUI"},
            ("LoadImage", 10): {"image": "example.png"},
        },
    ),
    id="img2img_cropped.png",
)
