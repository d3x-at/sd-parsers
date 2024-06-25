import pytest
from PIL import Image
from sd_parsers.data import Model, Prompt, Sampler
from sd_parsers.parsers import FooocusParser

from tests.tools import RESOURCE_PATH

SAMPLERS = [
    Sampler(
        name="dpmpp_2m_sde_gpu",
        parameters={
            "cfg_scale": 4,
            "scheduler": "karras",
            "seed": "6952411511246973023",
            "sharpness": 2,
            "steps": 30,
        },
        sampler_id=None,
        model=Model(
            name="juggernautXL_v8Rundiffusion", hash="aeb7e9e689", model_id=None, metadata={}
        ),
        prompts=[Prompt(value="a smiling goldfish", prompt_id=1, metadata={})],
        negative_prompts=[],
    )
]

METADATA = {
    "adm_guidance": "(1.5, 0.8, 0.3)",
    "clip_skip": 2,
    "full_negative_prompt": [
        "(worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed, grayscale, bw, bad photo, bad photography, bad art:1.4), (watermark, signature, text font, username, error, logo, words, letters, digits, autograph, trademark, name:1.2), (blur, blurry, grainy), morbid, ugly, asymmetrical, mutated malformed, mutilated, poorly lit, bad shadow, draft, cropped, out of frame, cut off, censored, jpeg artifacts, out of focus, glitch, duplicate, (airbrushed, cartoon, anime, semi-realistic, cgi, render, blender, digital art, manga, amateur:1.3), (3D ,3D Game, 3D Game Scene, 3D Character:1.1), (bad hands, bad anatomy, bad body, bad face, bad teeth, bad arms, bad legs, deformities:1.3)",
        "anime, cartoon, graphic, (blur, blurry, bokeh), text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
    ],
    "full_prompt": [
        "cinematic still a smiling goldfish . emotional, harmonious, vignette, 4k epic detailed, shot on kodak, 35mm photo, sharp focus, high budget, cinemascope, moody, epic, gorgeous, film grain, grainy",
        "a smiling goldfish, deep focus, intricate, elegant, highly detailed, cinematic, still, dynamic background, professional fine composition, ambient light, magic, vivid colors, creative, positive, attractive, glossy, shiny, colorful, strong, sharp, heroic, awesome, determined, cute, epic, stunning, gorgeous, amazing, symmetry, great, perfect, excellent, complex",
    ],
    "loras": [],
    "metadata_scheme": "fooocus",
    "performance": "Speed",
    "prompt_expansion": "a smiling goldfish, deep focus, intricate, elegant, highly detailed, cinematic, still, dynamic background, professional fine composition, ambient light, magic, vivid colors, creative, positive, attractive, glossy, shiny, colorful, strong, sharp, heroic, awesome, determined, cute, epic, stunning, gorgeous, amazing, symmetry, great, perfect, excellent, complex",
    "refiner_model": "None",
    "refiner_switch": 0.5,
    "resolution": "(768, 1280)",
    "styles": "['Fooocus V2', 'Fooocus Enhance', 'Fooocus Sharp']",
    "vae": "Default (model)",
    "version": "Fooocus v2.4.3",
}

testdata = [
    pytest.param("fooocus1_cropped.png", (SAMPLERS, METADATA), id="fooocus1_cropped.png"),
]


@pytest.mark.parametrize("filename, expected", testdata)
def test_parse(filename: str, expected):
    expected_samplers, expected_metadata = expected

    parser = FooocusParser()
    with Image.open(RESOURCE_PATH / "parsers/Fooocus" / filename) as image:
        params = parser.read_parameters(image)

    samplers, metadata = parser.parse(*params)

    assert samplers == expected_samplers
    assert metadata == expected_metadata
