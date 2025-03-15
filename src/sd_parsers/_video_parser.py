import json
import logging
import ffmpeg

from .data import PromptInfo
from .exceptions import ParserError
from .parser import DEBUG
from .parsers import ComfyUIParser

logger = logging.getLogger(__name__)
parser = ComfyUIParser()


def parse_video(video_file: str):
    """experimental - try to parse video generation metadata"""
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
