import pytest
from sd_parsers.data import Model, Prompt, Sampler

PARAM = pytest.param(
    {
        "prompt": {
            "198": {
                "inputs": {
                    "model": "wan\\wan2.1_i2v_480P_14B_fp8_e4m3fn.safetensors",
                    "base_precision": "fp16",
                    "quantization": "fp8_e4m3fn",
                    "load_device": "offload_device",
                    "attention_mode": "sageattn",
                },
                "class_type": "WanVideoModelLoader",
                "_meta": {"title": "WanVideo Model Loader"},
            },
            "232": {
                "inputs": {"positive": ["234", 0], "negative": ["235", 0]},
                "class_type": "WanVideoTextEmbedBridge",
                "_meta": {"title": "WanVideo TextEmbed Bridge"},
            },
            "234": {
                "inputs": {
                    "text": "positive prompt",
                    "clip": ["233", 0],
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Positive Prompt"},
            },
            "235": {
                "inputs": {
                    "text": "negative prompt",
                    "clip": ["233", 0],
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Negative Prompt"},
            },
            "252": {
                "inputs": {
                    "steps": 30,
                    "cfg": 6.0,
                    "shift": 6.0,
                    "seed": 1234,
                    "force_offload": False,
                    "scheduler": "unipc",
                    "riflex_freq_index": 0,
                    "denoise_strength": 1.0,
                    "model": ["198", 0],
                    "text_embeds": ["232", 0],
                },
                "class_type": "WanVideoSampler",
                "_meta": {"title": "WanVideo Sampler"},
            },
        },
        "workflow": {"links": []},
    },
    (
        [
            Sampler(
                name="unipc",
                parameters={
                    "cfg_scale": 6.0,
                    "steps": 30,
                    "shift": 6.0,
                    "seed": 1234,
                    "force_offload": False,
                    "riflex_freq_index": 0,
                    "denoise_strength": 1.0,
                },
                sampler_id="252",
                model=Model(
                    name="wan\\wan2.1_i2v_480P_14B_fp8_e4m3fn.safetensors",
                    metadata={
                        "base_precision": "fp16",
                        "quantization": "fp8_e4m3fn",
                        "load_device": "offload_device",
                        "attention_mode": "sageattn",
                    },
                    model_id="198",
                ),
                prompts=[
                    Prompt(
                        value="positive prompt",
                        prompt_id="234",
                    )
                ],
                negative_prompts=[
                    Prompt(
                        value="negative prompt",
                        prompt_id="235",
                    )
                ],
            )
        ]
    ),
    id="WanVideo1",
)
