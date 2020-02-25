#!/bin/bash

import argparse
import cv2
import json
import numpy as np
from pathlib import Path
from PIL import Image
import pydicom
from pydicom.dataset import Dataset, FileDataset
import sys

DEFAULT_OUTPUT_DIR = Path(__file__).parent / Path("output")
JSON_SUFFIX = ".json"
DCM_SUFFIX = ".dcm"
JSON_DATA_ENTRY = "data"
JSON_IMAGE_ENTRY = "image"
JSON_META_ENTRY = "meta"
JSON_TEMPLATE_ENTRY = "template"


def json2dicom(input_filepath, output_filename):
    try:
        input_file = open(input_filepath, "r")
        input_json = json.loads(input_file.read())

        if not JSON_DATA_ENTRY in input_json:
            print("Cannot find mandatory JSON field name '{}' in '{}'".format(
                JSON_DATA_ENTRY, str(input_filepath)))
            return 4

        if not JSON_TEMPLATE_ENTRY in input_json:
            print("Cannot find mandatory JSON field name '{}' in '{}'".format(
                JSON_TEMPLATE_ENTRY, str(input_filepath)))
            return 5

        template_filepath = Path(input_json[JSON_TEMPLATE_ENTRY])
        if not template_filepath.exists():
            print("'{}' does not exists, abort json2dicom execution!".format(
                template_filepath))
            return 6
        if not template_filepath.is_file():
            print("'{}' is not a file, abort json2dicom execution!".format(
                template_filepath))
            return 7

        template_file = open(template_filepath, "r")
        current_json = json.loads(template_file.read())

        # Override template object
        current_json[JSON_DATA_ENTRY].update(input_json[JSON_DATA_ENTRY])
        dicom_dataset = Dataset().from_json(current_json[JSON_DATA_ENTRY])
        dicom_meta = Dataset().from_json(current_json[JSON_META_ENTRY])

        image_json_data = input_json[JSON_IMAGE_ENTRY]
        if image_json_data:
            if image_json_data:
                image_filepath = Path(image_json_data)
                if not image_filepath.exists():
                    print("{} does not exists, abort json2dicom execution!".format(
                        image_filepath))
                    return 1
                if not image_filepath.is_file():
                    print("{} is not a file, abort json2dicom execution!".format(
                        image_filepath))
                    return 2

                image = cv2.imread(str(image_filepath),
                                   flags=cv2.IMREAD_UNCHANGED)
                shape = image.shape
                bit_depth = None
                if len(shape) < 3:
                    bit_depth = 8 * image.dtype.itemsize
                else:
                    print("Cannot manage image with bit depth > 16 bits")
                    return 5

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
                DEFAULT_OUTPUT_DIR / dicom_dataset.SOPInstanceUID).with_suffix(DCM_SUFFIX)

        ds = FileDataset(output_filepath.stem,
                         dicom_dataset, file_meta=dicom_meta, preamble=b"\0" * 128)
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.save_as(str(output_filepath))
    except FileNotFoundError as file_not_found_error:
        print("Cannot read input file, because {}".format(file_not_found_error))
        return 3
    except SystemError as system_error:
        print("Cannot read image file, because {}".format(system_error))
        return 6

    return 0


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
        print("{} does not exists, abort json2dicom execution!".format(input_filepath))
        return 1
    if not input_filepath.is_file():
        print("{} is not a file, abort json2dicom execution!".format(input_filepath))
        return 2

    return json2dicom(input_filepath,
                      args.output_filename)


if __name__ == "__main__":
    """Entry point of the script
    """
    exit(main())
