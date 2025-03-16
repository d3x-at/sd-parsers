"""
experimental - try to parse video generation metadata

uses only the ComfyUI parser for now
structured parsing will most likely return unusable data - check raw_parameters instead.

your system needs ffmpeg installed for this to work

install ffmpeg support with:
pip3 install ffmpeg-python
"""

import json
import logging
import ffmpeg
import sys
from pprint import pprint

from sd_parsers.data import PromptInfo
from sd_parsers.exceptions import ParserError
from sd_parsers.parser import DEBUG
from sd_parsers.parsers import ComfyUIParser

logger = logging.getLogger(__name__)
parser = ComfyUIParser()


def parse_video(video_file: str):
    res = ffmpeg.probe(video_file)

    try:
        comment = res["format"]["tags"]["comment"]
        parameters = json.loads(comment)
    except (KeyError, TypeError, json.JSONDecodeError):
        return None

    try:
        generator, samplers, metadata = parser.parse(parameters)
        return PromptInfo(generator, samplers, metadata, parameters)
    except ParserError as error:
        if DEBUG:
            logger.debug("error in parser[%s]: %s", type(parser), error)

    return None


if __name__ == "__main__":
    try:
        prompt_info = parse_video(sys.argv[1])
    except IndexError:
        print("usage: parse_video <video_file.mp4>")

    if prompt_info is None:
        print("no metadata found")
    else:
        # pprint(prompt_info)  # to check structured response
        pprint(prompt_info.raw_parameters)
