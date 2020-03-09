#!/usr/bin/env python3

import argparse
import cv2
import json
import numpy as np
import logging
from pathlib import Path
from PIL import Image
import pydicom
from pydicom.dataset import Dataset, FileDataset
import sys
from constants import DicomConstants, JsonConstants, PngConstants

DEFAULT_OUTPUT_DIR = Path(__file__).parent / Path("output")
logger = logging.getLogger()


def json2dicom(input_filepath, output_filename):
    try:
        input_file = open(input_filepath, "r")
        input_json = json.loads(input_file.read())

        if not JsonConstants.TEMPLATE.value in input_json:
            error = "Cannot find mandatory JSON field name '{}' in '{}'".format(
                JsonConstants.TEMPLATE.value, str(input_filepath))
            raise ValueError(error)

        template_filepath = Path(input_json[JsonConstants.TEMPLATE.value])
        if not template_filepath.exists():
            error = "'{}' template file does not exists, abort json2dicom execution!".format(
                template_filepath)
            raise ValueError(error)
        if not template_filepath.is_file():
            error = "'{}' template file is not a file, abort json2dicom execution!".format(
                template_filepath)
            raise ValueError(error)

        template_file = open(template_filepath, "r")
        current_json = json.loads(template_file.read())

        # Override template object
        current_json[JsonConstants.DATA.value].update(
            input_json[JsonConstants.DATA.value])
        dicom_dataset = Dataset().from_json(
            current_json[JsonConstants.DATA.value])
        dicom_meta = Dataset().from_json(
            current_json[JsonConstants.META.value])

        image_json_data = input_json[JsonConstants.IMAGE.value]
        if image_json_data:
            if image_json_data:
                image_filepath = Path(image_json_data)
                if not image_filepath.exists():
                    error = "'{}' image file does not exists, abort json2dicom execution!".format(
                        image_filepath)
                    raise ValueError(error)
            if not image_filepath.is_file():
                error = "'{}' image is not a file, abort json2dicom execution!".format(
                    image_filepath)
                raise ValueError(error)

            image = cv2.imread(str(image_filepath),
                               flags=cv2.IMREAD_UNCHANGED)
            shape = image.shape
            bit_depth = None
            if len(shape) < 3:
                bit_depth = 8 * image.dtype.itemsize
            else:
                error = "Cannot manage image with bit depth > 16 bits"
                raise ValueError(error)

            dicom_dataset.BitsAllocated = bit_depth
            dicom_dataset.BitsStored = bit_depth
            dicom_dataset.HighBits = bit_depth - 1
            dicom_dataset.WindowCenter = pow(2, bit_depth - 1)
            dicom_dataset.WindowWidth = pow(2, bit_depth) - 1
            dicom_dataset.Rows = shape[0]
            dicom_dataset.Columns = shape[1]
            dicom_dataset.PixelData = image

        # Format output filepath
        output_filepath = None
        if output_filename:
            output_filepath = (DEFAULT_OUTPUT_DIR / Path(output_filename))
        else:
            output_filepath = (
                DEFAULT_OUTPUT_DIR / dicom_dataset.SOPInstanceUID).with_suffix(DicomConstants.SUFFIX.value)

        ds = FileDataset(output_filepath.stem,
                         dicom_dataset, file_meta=dicom_meta, preamble=b"\0" * 128)
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.save_as(str(output_filepath))
        print("Output file has been writed at: '{}'".format(output_filepath))
    except (FileNotFoundError, SystemError) as error:
        raise error


def main():
    """main
    Extract all informations from arguments parser
    If all mandatories data are provided, we launch
    the converter

    Returns:
        [int] -- Script exit code
    """
    parser = argparse.ArgumentParser()

    # Positional argument
    parser.add_argument(
        "input_json_file",
        type=str,
        help="json to convert to dicom")

    # Optionals arguments
    parser.add_argument(
        "-o",
        "--output_filename",
        type=str,
        help="output filename",
        default=None)

    args = parser.parse_args()

    input_filepath = Path(args.input_json_file)
    if not input_filepath.exists():
        error = "{} does not exists, abort json2dicom execution!".format(
            input_filepath)
        raise ValueError(error)
    if not input_filepath.is_file():
        error = "{} is not a file, abort json2dicom execution!".format(
            input_filepath)
        raise ValueError(error)

    try:
        json2dicom(input_filepath,
                   args.output_filename)
    except Exception as error:
        raise error


if __name__ == "__main__":
    """Entry point of the script
    """
    try:
        main()
        exit(0)
    except ValueError as error:
        logger.exception(error)
        exit(1)
