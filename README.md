*DicomJSON*
=======

*DicomJSON* is a [pydicom](https://github.com/pydicom/pydicom) python package overlay.
It was made for simplify DICOM file generation based on template (JSON) and image (PNG) files.

You will find in this repository two scripts.

**dicom2json**
* Convert *.dcm file to two files
  * One JSON file describe all DICOM fields
  * One PNG file represent the image available in the PixelData DICOM field

```
usage: dicom2json.py [-h] [-rdf REMOVE_DICOM_FIELDS [REMOVE_DICOM_FIELDS ...]] input_file

positional arguments:
  input_file            dicom to convert to json

optional arguments:
  -h, --help            show this help message and exit
  -rdf REMOVE_DICOM_FIELDS [REMOVE_DICOM_FIELDS ...], --remove_dicom_fields REMOVE_DICOM_FIELDS [REMOVE_DICOM_FIELDS ...]
                        remove DICOM fields after extraction
```

**json2dicom**
* Convert one *.json file to one *.dcm file
  * You can find an example in the 'input' folder named 'test.json'
    * This file contains the following entries:
      * "template": Path to JSON file extracted from dicom2json.py script
        * It will be used as template for your DICOM generation
      * "data": DICOM data described as you can see in the dicom2json.py output file. If a data is present in this field, you'll override the DICOM field value available in "template".
        ```
        For example, if you want to override PatientName DICOM field value, you need to write in your *.json file:
        {
          "data": {
              "00100010": {
                  "Value": [
                      {
                          "Alphabetic": "John^Doe"
                      }
                  ],
                  "vr": "PN"
              }
          }
        }
        ```
      * "meta": DICOM metadata described as you can see in the dicom2json.py output file. If a data is present in this field, you'll override the DICOM field value available in "template".
      * "image": Image filepath to override the following DICOM fields:
        * BitsAllocated
        * BitsStored
        * HighBits
        * WindowCenter
        * WindowWidth
        * Rows
        * Columns
        * PixelData

```
usage: json2dicom.py [-h] [-o OUTPUT_FILENAME] input_json_file

positional arguments:
  input_json_file       json to convert to dicom

optional arguments:
  -h, --help            show this help message and exit       
  -o OUTPUT_FILENAME, --output_filename OUTPUT_FILENAME       
                        output filename
```

Documentation
-------------
You can install all requirements for this repository using the following command:
```
pip install -r requirements.txt
```

Known issues
-------------
The pydicom Python library cannot extract DICOM fields with 'DS' as VR type and field value with only '\' as characters