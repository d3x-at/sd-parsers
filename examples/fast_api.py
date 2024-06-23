"""
Return raw generation metadata when an image generated with supported SD software is submitted.

usage: uvicorn fast_api:app
test: curl -X "POST" http://127.0.0.1:8000/api/parse -F "image=@/path/to/image.png"
"""
from fastapi import FastAPI, UploadFile
from PIL import Image
from sd_parsers import ParserManager

# don't do this in production!
from sd_parsers.parsers import *  # noqa: F403

app = FastAPI()

# reorder the used parsers so that the least complex metadata checks are done last (to reduce false positives)
managed_parsers = [NovelAIParser, ComfyUIParser, InvokeAIParser, FooocusParser, AUTOMATIC1111Parser]  # noqa: F405

parser_manager = ParserManager(managed_parsers=managed_parsers)


@app.post("/api/parse")
def parse(image: UploadFile):
    with Image.open(image.file) as _image:
        params = parser_manager.read_parameters(_image)

    if params is None:
        return {"success": False}

    parser, metadata, _ = params
    return {"success": True, "parser": parser.generator, "metadata": metadata}
