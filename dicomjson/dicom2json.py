#!/bin/bash

import argparse
import json
from pathlib import Path
import pydicom
from pydicom.dataset import Dataset, FileDataset

DEFAULT_OUTPUT_DIR = Path(__file__).parent / Path("output")
JSON_SUFFIX = ".json"


def my_json_dumps(data):
    """my_json_dumps
    JSON formatter

    Arguments:
        data {str} -- Data to JSON beautify

    Returns:
        str -- Data beautified
    """
    return json.dumps(data, indent=4, sort_keys=True)


def dicom2json(input_file, output_filename, remove_dicom_fields):
    """dicom2json
    Convert DICOM file to JSON using pydicom library

    Arguments:
        input_file {str} -- DICOM file location
        output_filename {str} -- JSON output file location
        remove_dicom_fields {list} -- DICOM field name to not save in JSON
    """
    try:
        dicom_dataset = pydicom.dcmread(str(input_file))

        if remove_dicom_fields:
            for dicom_fields_name in remove_dicom_fields:
                if dicom_dataset.get(dicom_fields_name):
                    dicom_dataset.pop(dicom_fields_name)
                else:
                    print("Unrecognized DICOM field named '{}'".format(
                        dicom_fields_name))

        # Convert FileDataset to JSON object
        dicom_dataset_to_json_meta = dicom_dataset.file_meta.to_json_dict()
        dicom_dataset_to_json = dicom_dataset.to_json_dict()

        # Format output filepath
        output_filepath = None
        if output_filename:
            output_filepath = (DEFAULT_OUTPUT_DIR / Path(output_filename))
        else:
            output_filepath = (
                DEFAULT_OUTPUT_DIR / dicom_dataset.SOPInstanceUID).with_suffix(JSON_SUFFIX)

        # Write JSON file
        dicom_json_file = open(output_filepath, "w")
        dicom_json_file.write(my_json_dumps(
            {"meta": dicom_dataset_to_json_meta, "data": dicom_dataset_to_json}))
        dicom_json_file.close()
        print("Output file has been writed at: '{}'".format(output_filepath))
    except FileNotFoundError as file_not_found_error:
        print(file_not_found_error)


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
        "input_file",
        type=str,
        help="dicom to convert to json")

    # Optionals arguments
    parser.add_argument(
        "-o",
        "--output_filename",
        type=str,
        help="output filename",
        default=None)
    parser.add_argument(
        "-rdf",
        "--remove_dicom_fields",
        nargs='+',
        type=str,
        help="remove DICOM fields after extraction",
        default=None)

    args = parser.parse_args()

    input_filepath = Path(args.input_file)
    if not input_filepath.exists():
        print("{} does not exists, abort dicom2json execution!".format(input_filepath))
        return 1
    if not input_filepath.is_file():
        print("{} is not a file, abort dicom2json execution!".format(input_filepath))
        return 2

    return dicom2json(input_filepath,
                      args.output_filename,
                      args.remove_dicom_fields)


if __name__ == "__main__":
    """Entry point of the script
    """
    exit(main())
