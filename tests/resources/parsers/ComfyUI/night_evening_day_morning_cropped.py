import pytest
from sd_parsers.data import Model, Prompt, Sampler

PARAM = pytest.param(
    "night_evening_day_morning_cropped.png",
    (
        [
            Sampler(
                name="dpmpp_sde",
                parameters={
                    "cfg": 8.5,
                    "denoise": 1.0,
                    "scheduler": "normal",
                    "seed": 335608130539327,
                    "steps": 13,
                },
                sampler_id=3,
                model=Model(model_id=45, name="Anything-V3.0.ckpt", hash=None),
                prompts=[
                    Prompt(
                        value="(best quality) (daytime:1.2) sky (blue)",
                        prompt_id=17,
                        metadata={
                            ("ConditioningCombine", 19): {},
                            ("ConditioningCombine", 12): {},
                            ("ConditioningSetArea", 11): {
                                "width": 704,
                                "height": 384,
                                "x": 0,
                                "y": 512,
                                "strength": 1.0,
                            },
                        },
                    ),
                    Prompt(
                        value="(best quality) (night:1.3) (darkness) sky (black) (stars:1.2) "
                        "(galaxy:1.2) (space) (universe)",
                        prompt_id=14,
                        metadata={
                            ("ConditioningCombine", 19): {},
                            ("ConditioningCombine", 12): {},
                            ("ConditioningCombine", 35): {},
                            ("ConditioningSetArea", 34): {
                                "width": 704,
                                "height": 384,
                                "x": 0,
                                "y": 0,
                                "strength": 1.2000000000000002,
                            },
                        },
                    ),
                    Prompt(
                        value="(best quality) (evening:1.2) (sky:1.2) (clouds) (colorful) "
                        "(HDR:1.2) (sunset:1.3)",
                        prompt_id=13,
                        metadata={
                            ("ConditioningCombine", 19): {},
                            ("ConditioningCombine", 12): {},
                            ("ConditioningCombine", 35): {},
                            ("ConditioningSetArea", 18): {
                                "width": 704,
                                "height": 384,
                                "x": 0,
                                "y": 320,
                                "strength": 1.0,
                            },
                        },
                    ),
                    Prompt(
                        value="(masterpiece) (best quality) morning sky",
                        prompt_id=33,
                        metadata={
                            ("ConditioningCombine", 19): {},
                            ("ConditioningCombine", 10): {},
                            ("ConditioningSetArea", 15): {
                                "width": 704,
                                "height": 384,
                                "x": 0,
                                "y": 704,
                                "strength": 1.0,
                            },
                        },
                    ),
                    Prompt(
                        value="(masterpiece) (best quality) beautiful landscape breathtaking "
                        "amazing view nature photograph forest mountains ocean (sky) "
                        "national park scenery",
                        prompt_id=6,
                        metadata={
                            ("ConditioningCombine", 19): {},
                            ("ConditioningCombine", 10): {},
                        },
                    ),
                ],
                negative_prompts=[
                    Prompt(
                        value="(hands), text, error, cropped, (worst "
                        "quality:1.2), (low quality:1.2), "
                        "normal quality, (jpeg artifacts:1.3), "
                        "signature, watermark, username, "
                        "blurry, artist name, monochrome, "
                        "sketch, censorship, censor, "
                        "(copyright:1.2), extra legs, "
                        "(forehead mark) (depth of field) "
                        "(emotionless) (penis) (pumpkin)",
                        prompt_id=7,
                    )
                ],
            ),
            Sampler(
                name="dpmpp_2m",
                parameters={
                    "cfg": 7.0,
                    "denoise": 0.5,
                    "scheduler": "simple",
                    "seed": 1122440447966177,
                    "steps": 14,
                },
                sampler_id=24,
                model=Model(
                    model_id=46,
                    name="AbyssOrangeMix2_hard.safetensors",
                    hash=None,
                ),
                prompts=[
                    Prompt(
                        value="(best quality) beautiful (HDR:1.2) "
                        "(realistic:1.2) landscape breathtaking amazing "
                        "view nature scenery photograph forest "
                        "mountains ocean daytime night evening morning, "
                        "(sky:1.2)",
                        prompt_id=26,
                    )
                ],
                negative_prompts=[
                    Prompt(
                        value="(hands), text, error, cropped, (worst "
                        "quality:1.2), (low quality:1.2), "
                        "normal quality, (jpeg artifacts:1.3), "
                        "signature, watermark, username, "
                        "blurry, artist name, monochrome, "
                        "sketch, censorship, censor, "
                        "(copyright:1.2), extra legs, "
                        "(forehead mark) (depth of field) "
                        "(emotionless) (penis) (pumpkin)",
                        prompt_id=27,
                    )
                ],
            ),
        ],
        {
            ("EmptyLatentImage", 5): {"width": 704, "height": 1280, "batch_size": 1},
            ("SaveImage", 9): {"filename_prefix": "ComfyUI"},
            ("VAELoader", 20): {"vae_name": "vae-ft-mse-840000-ema-pruned.safetensors"},
            ("LatentUpscale", 22): {
                "upscale_method": "nearest-exact",
                "width": 1088,
                "height": 1920,
                "crop": "disabled",
            },
            ("SaveImage", 32): {"filename_prefix": "ComfyUI"},
            ("CLIPSetLastLayer", 44): {"stop_at_clip_layer": -2},
            ("CLIPSetLastLayer", 47): {"stop_at_clip_layer": -2},
        },
    ),
    id="night_evening_day_morning_cropped.png",
)
