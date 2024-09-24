"""
Return raw generation metadata when an image generated with supported SD software is submitted.

usage: uvicorn fast_api:app
test: curl -X "POST" http://127.0.0.1:8000/api/parse -F "image=@/path/to/image.png"
"""

from fastapi import FastAPI, UploadFile
from PIL import Image
from sd_parsers import ParserManager

app = FastAPI()

parser_manager = ParserManager()


@app.post("/api/parse")
def parse(image: UploadFile):
    with Image.open(image.file) as _image:
        params = parser_manager.read_parameters(_image)

    if params is None:
        return {"success": False}

    parser, metadata, _ = params
    return {"success": True, "parser": type(parser).__name__, "metadata": metadata}
