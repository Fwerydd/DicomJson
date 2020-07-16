#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import logging
import cv2
from pydicom.dataset import Dataset, FileDataset
from constants import DicomConstants, JsonConstants, PngConstants

DEFAULT_OUTPUT_DIR = Path(__file__).parent / Path("output")
# Define Formatter
log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s") # pylint: disable=C0103
# Get basic logger
logger = logging.getLogger() # pylint: disable=C0103
logger.setLevel(logging.DEBUG)
# Define output file logger
file_handler = logging.FileHandler('json2dicom.log') # pylint: disable=C0103
file_handler.setFormatter(log_formatter)
# Define output console logger
console_handler = logging.StreamHandler() # pylint: disable=C0103
console_handler.setFormatter(log_formatter)
# Associate console and file loggers to the root logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def convert_data_to_dicom(input_filepath, input_json):
    """
    Convert data available in input_json to DICOM file

    Args:
        input_filepath (str): Input JSON file
        input_json (object): Input file description (see README.md)

    Raises:
        ValueError: Invalid value in the JSON file
    """
    if not JsonConstants.TEMPLATE.value in input_json:
        template_error = "Cannot find mandatory JSON field name '{}' in '{}'".format(
            JsonConstants.TEMPLATE.value, str(input_filepath))
        raise ValueError(template_error)

    template_filepath = Path(input_json[JsonConstants.TEMPLATE.value])
    if not template_filepath.exists():
        template_not_exists = "'{}' template file does not exists, abort json2dicom execution!".format(
            input_filepath)
        raise ValueError(template_not_exists)
    if not template_filepath.is_file():
        template_is_not_file = "'{}' template file is not a file, abort json2dicom execution!".format(
            input_filepath)
        raise ValueError(template_is_not_file)

    template_file = open(template_filepath, "r")
    current_json = json.loads(template_file.read())

    # Override template object if 'data' key is present
    if JsonConstants.DATA.value in input_json:
        current_json[JsonConstants.DATA.value].update(
            input_json[JsonConstants.DATA.value])

    # Check if a specific output filename is specified
    output_filename = None
    if JsonConstants.OUTPUT.value in input_json:
        output_filename = input_json[JsonConstants.OUTPUT.value]

    dicom_dataset = Dataset()
    dicom_meta = Dataset()

    # Parse each data DICOM value, to test if valid
    data_dict = current_json[JsonConstants.DATA.value]
    dicom_fields_with_error = []
    for dicom_json_value in data_dict:
        dicom_dict = {
            dicom_json_value: data_dict.get(dicom_json_value)}
        try:
            Dataset().from_json(json.dumps(dicom_dict))
        except (json.JSONDecodeError, TypeError, ValueError) as exception_error:
            dicom_fields_with_error.append(dicom_json_value)
            logger.warning("%s cannot add the field '%s', because the value is not standard with the VR: '%s'", input_filepath, dicom_json_value, dicom_dict)
    # Remove error DICOM fields
    for dicom_field_with_error in dicom_fields_with_error:
        del data_dict[dicom_field_with_error]

    try:
        dicom_dataset = Dataset().from_json(data_dict)
        dicom_meta = Dataset().from_json(
            current_json[JsonConstants.META.value])
    except (json.JSONDecodeError, TypeError, ValueError) as exception_error:
        exception_error = "Error encountered during JSON parsing: \"{}\", abort json2dicom execution!".format(
            exception_error)
        raise ValueError(exception_error)

    # Override image in the DICOM if 'image' key is present
    if JsonConstants.IMAGE.value in input_json:
        image_json_data = input_json[JsonConstants.IMAGE.value]
        if image_json_data:
            if image_json_data:
                image_filepath = Path(image_json_data)
                if not image_filepath.exists():
                    image_not_exists = "'{}' image file does not exists, abort json2dicom execution!".format(
                        image_filepath)
                    raise ValueError(image_not_exists)
            if not image_filepath.is_file():
                image_is_not_file = "'{}' image is not a file, abort json2dicom execution!".format(
                    image_filepath)
                raise ValueError(image_is_not_file)

            image = cv2.imread(str(image_filepath),
                                flags=cv2.IMREAD_UNCHANGED)
            shape = image.shape
            bit_depth = None
            if len(shape) < 3:
                bit_depth = 8 * image.dtype.itemsize
            else:
                raise ValueError("Cannot manage image with bit depth > 16 bits")

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

    dataset = FileDataset(output_filepath.stem,
                        dicom_dataset, file_meta=dicom_meta, preamble=b"\0" * 128)
    dataset.is_little_endian = True
    dataset.is_implicit_VR = False
    dataset.save_as(str(output_filepath))
    logger.debug("Output file has been writed at: '%s'", output_filepath)


def json2dicom(input_filepath):
    """
    Convert JSON input file to DICOM

    Args:
        input_filepath (str): Input JSON filepath

    Raises:
        error: Error encountered during conversion
    """
    try:
        input_file = open(input_filepath, "r")
        input_json = json.loads(input_file.read())

        if isinstance(input_json, list):
            for json_object in input_json:
                try:
                    convert_data_to_dicom(input_filepath, json_object)
                except (ValueError) as error:
                    raise error
        else:
            try:
                convert_data_to_dicom(input_filepath, input_json)
            except (ValueError) as error:
                raise error
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

    args = parser.parse_args()

    input_filepath = Path(args.input_json_file)
    if not input_filepath.exists():
        input_not_exists = "{} does not exists, abort json2dicom execution!".format(
            input_filepath)
        raise ValueError(input_not_exists)
    if not input_filepath.is_file():
        input_is_not_file = "{} is not a file, abort json2dicom execution!".format(
            input_filepath)
        raise ValueError(input_is_not_file)

    try:
        json2dicom(input_filepath)
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
