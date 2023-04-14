"""
return metadata provided by sdparsers.
usage: uvicorn fast_api:app
test: curl -X "POST" http://127.0.0.1:8000/api/parse -F "file=@/path/to/image.png"
"""
import io
import sdparsers as parser
import simplejson as json
from fastapi import FastAPI, File, UploadFile, Response

app = FastAPI()
parser_manager = parser.ParserManager()


@app.post("/api/parse")
def parse(image: UploadFile = File(...)):
    with io.BytesIO(image.file.read()) as fp:
        res = parser_manager.parse(fp)
    if res:
        return Response(content=json.dumps(res), media_type="application/json")
    return {"success": False}
