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
usage: dicom2json.py [-h] input_file [-rdf REMOVE_DICOM_FIELDS [REMOVE_DICOM_FIELDS ...]] 

positional arguments:
  input_file            dicom to convert to json

optional arguments:
  -h, --help            show this help message and exit
  -rdf REMOVE_DICOM_FIELDS [REMOVE_DICOM_FIELDS ...], --remove_dicom_fields REMOVE_DICOM_FIELDS [REMOVE_DICOM_FIELDS ...]
                        remove DICOM fields after extraction. The list of possible values is available in the file '_dicom_dict.py' at the root of the folder where  
                        the 'Keyword' for each field is specified.
```

**json2dicom**
* Convert DICOM object(s) describe in a json file
  * You can find an example in the 'input' folder named 'test.json'
    * This file contains the following entries for one object. Note: You can have only one object or a array of objects in this file!
      * "template": Path to JSON file extracted from dicom2json.py script
        * It will be used as template for your DICOM generation
      * "image": Path to PNG file extracted from dicom2json.py script
        * It will be used as image for your DICOM generation. This image override the following DICOM fields
         * BitsAllocated
         * BitsStored
         * HighBits
         * Rows
         * Columns
         * PixelData
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
```
usage: json2dicom.py [-h] input_json_file [-o OUTPUT_FILENAME] 

positional arguments:
  input_json_file       json to convert to dicom

optional arguments:
  -h, --help            show this help message and exit
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
