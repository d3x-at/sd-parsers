import pytest
from sd_parsers import Model, Prompt, Sampler

MODELS = [Model(name="juggernautXL", parameters={"base_model": "sdxl", "model_type": "main"})]

PROMPTS = [Prompt(value="digital artwork, oil painting. painterly brushstrokes, holidays,")]

NEGATIVE_PROMPTS = [
    Prompt(
        value=(
            "grainy+, photo, oversaturated, overexposed, blurry, "
            "compressed jpg+, noisy++, unfocused , black and white"
        )
    )
]

PARAM = pytest.param(
    "invokeai_imeta1.png",
    (
        Sampler(
            name="euler",
            parameters={
                "seed": 3293022630,
                "cfg_scale": 8.0,
                "cfg_rescale_multiplier": 0.0,
                "steps": 35,
            },
            model=MODELS[0],
            prompts=PROMPTS,
            negative_prompts=NEGATIVE_PROMPTS,
        ),
        set(MODELS),
        set(PROMPTS),
        set(NEGATIVE_PROMPTS),
        {
            "generation_mode": "sdxl_txt2img",
            "width": 1024,
            "height": 1024,
            "size": "1024x1024",
            "rand_device": "cpu",
            "ipAdapters": [
                {
                    "image": {"image_name": "21b3ddb9-089b-49fd-b074-0b9fdac3ab3e.png"},
                    "ip_adapter_model": {
                        "model_name": "ip-adapter-plus_sdxl_vit-h",
                        "base_model": "sdxl",
                    },
                    "weight": 0.45,
                    "begin_step_percent": 0.0,
                    "end_step_percent": 1.0,
                }
            ],
            "vae": {"model_name": "VAEFix", "base_model": "sdxl"},
            "positive_style_prompt": "",
            "negative_style_prompt": "",
        },
    ),
    id="invokeai_imeta1.png",
)
