import pytest
from sd_parsers.data import Model, Prompt, Sampler

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
            model=Model(name="juggernautXL", metadata={"base_model": "sdxl", "model_type": "main"}),
            prompts=[Prompt(1, "digital artwork, oil painting. painterly brushstrokes, holidays,")],
            negative_prompts=[
                Prompt(
                    1,
                    (
                        "grainy+, photo, oversaturated, overexposed, blurry, "
                        "compressed jpg+, noisy++, unfocused , black and white"
                    ),
                )
            ],
        ),
        {
            "generation_mode": "sdxl_txt2img",
            "width": 1024,
            "height": 1024,
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
