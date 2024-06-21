"""Errors that may or may not happen during the image metadata parsing."""


class ParserError(Exception):
    """something went wrong while parsing the data"""


class MetadataError(ParserError):
    """metadata did not match our expectations - can be safely ignored"""
