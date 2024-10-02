"""
Return raw generation metadata when an image generated with supported SD software is submitted.

usage: uvicorn fast_api:app
test: curl -X "POST" http://127.0.0.1:8000/api/parse -F "image=@/path/to/image.png"
"""

from fastapi import FastAPI, UploadFile
from sd_parsers import ParserManager

app = FastAPI()

parser_manager = ParserManager()


@app.post("/api/parse")
def parse(image: UploadFile):
    # read_parameters returns each parser that might be able to interpret the images' metadata
    # parsers are tried in order of parameter complexity (to reduce false positives)
    params_iter = iter(parser_manager.read_parameters(image.file))

    try:
        # read_parameters yields (parser, parameters, parsing_context)
        # picking the first entry and ignoring what follows increases speed but reduces accuracy
        parser, parameters, parsing_context = next(params_iter)

        # allowing the parser to further process the returned parameters increases accuracy.
        # (see ParserManager.parse() implementation)
        #
        # try:
        #     generator, samplers, metadata = parser.parse(parameters, parsing_context)
        # except ParserError as error:
        #     ...

        return {"success": True, "parser": type(parser).__name__, "metadata": parameters}

    except StopIteration:
        return {"success": False}
