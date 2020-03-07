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
    META = "meta"
    DATA = "data"
    TEMPLATE = "template"
    IMAGE = "image"
    SUFFIX = ".json"


class PngConstants(Enum):
    """PngConstants
    Constants associated to PNG data
    """
    SUFFIX = ".png"
