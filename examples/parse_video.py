"""
experimental - try to parse video generation metadata

uses only the ComfyUI parser for now
structured parsing will most likely return unusable data - check raw_parameters instead.

your system needs ffmpeg installed for this to work

install ffmpeg support with:
pip3 install ffmpeg-python
"""

import json
import ffmpeg
import sys
from pprint import pprint

from sd_parsers.exceptions import ParserError
from sd_parsers.parsers import ComfyUIParser

parser = ComfyUIParser()


def parse_video(video_file: str):
    res = ffmpeg.probe(video_file)

    try:
        comment = res["format"]["tags"]["comment"]
        parameters = json.loads(comment)
    except (KeyError, TypeError, json.JSONDecodeError):
        return None

    try:
        return parser.parse(parameters)
    except ParserError as error:
        print("error in parser: ", error)

    return None


if __name__ == "__main__":
    try:
        prompt_info = parse_video(sys.argv[1])
    except IndexError:
        print("usage: parse_video <video_file.mp4>")
        sys.exit(1)

    if prompt_info is None:
        print("no metadata found")
    else:
        pprint(prompt_info)
