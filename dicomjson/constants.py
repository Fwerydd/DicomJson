"""constants
Contains constants for scripts
"""

from enum import Enum


class DicomConstants(Enum):
    """DicomConstants
    Constants associated to DICOM data
    """
    SUFFIX = ".dcm"


class JsonConstants(Enum):
    """JsonConstants
    Constants associated to JSON data
    """
    DATA = "data"
    IMAGE = "image"
    META = "meta"
    OUTPUT = "output"
    SUFFIX = ".json"
    TEMPLATE = "template"


class PngConstants(Enum):
    """PngConstants
    Constants associated to PNG data
    """
    SUFFIX = ".png"
