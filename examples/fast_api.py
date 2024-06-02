"""
return metadata provided by sdparsers.
usage: uvicorn fast_api:app
test: curl -X "POST" http://127.0.0.1:8000/api/parse -F "image=@/path/to/image.png"
"""
from fastapi import FastAPI, UploadFile
from sd_parsers import ParserManager

app = FastAPI()
parser_manager = ParserManager(lazy_read=True)
# lazy_read parameter available in sd-parsers >= 0.3.1rc1
#
# use lazy read to skip detailed metadata extraction
# warning: `parameters` can contain "garbage" information
# as some metadata checks are skipped with lazy_read


@app.post("/api/parse")
def parse(image: UploadFile):
    image_data = parser_manager.parse(image.file)
    if image_data:
        return {"success": True, "parameters": image_data.parameters}
    return {"success": False}
