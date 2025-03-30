import pytest
from sd_parsers import extractors
from sd_parsers.data import Model, Prompt, Sampler


PARAM = pytest.param(
    "automatic1111_stealth.png",
    extractors.png_stenographic_alpha,
    [
        Sampler(
            name="Euler",
            parameters={
                "scheduler": "Automatic",
                "cfg_scale": "7",
                "seed": "2015833630",
                "steps": "20",
            },
            model=Model(name="realisticVisionV51_v51VAE", hash="15012c538f"),
            prompts=[Prompt("a circle")],
            negative_prompts=[Prompt("a square")],
        )
    ],
    {
        "Clip skip": "2",
        "Size": "64x64",
        "Version": "v1.9.4-169-ga30b19dd",
    },
    id="automatic1111_stealth.png",
)
