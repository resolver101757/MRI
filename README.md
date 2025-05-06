# DICOM MRI Processing for VLM Analysis

This project contains scripts to extract and process DICOM MRI images for analysis with Vision Language Models (VLMs).

## Scripts

1. **analyze_dicom.py** - Basic script to analyze a single DICOM file and print its metadata.
2. **extract_dicom_for_vlm.py** - Main script to extract all DICOM files from a directory, convert them to PNG, and organize them by series.
3. **create_report.py** - Creates an HTML report of the extracted images for easy viewing.

## Features

- Extracts DICOM image data and converts to PNG format
- Maintains organizing by MRI series
- Applies proper windowing to optimize image contrast
- Anonymizes patient data
- Preserves relevant metadata in text files
- Organizes output by series with series information
- Creates HTML report with sample images from each series

## Usage

### 1. Analyze a Single DICOM File

```
python analyze_dicom.py
```

This script analyzes the first DICOM file it finds in the input directory and prints basic metadata.

### 2. Extract All DICOM Files

```
python extract_dicom_for_vlm.py
```

This script:
- Reads all DICOM files from the input directory
- Organizes them by series
- Converts them to PNG images with proper windowing
- Creates anonymized copies of the original DICOM files
- Saves metadata for each image

### 3. Create an HTML Report

```
python create_report.py
```

This script creates an HTML report with:
- Information about each series
- Sample images from each series
- Links to all images in each series

## Output Structure

```
extracted_for_vlm/
├── anonymized_dicoms/        # Anonymized DICOM files
├── [SeriesName1]_[UID]/      # Directory for each series
│   ├── slice_0000.png        # PNG image
│   ├── slice_0000_metadata.txt  # Metadata for this image
│   ├── ...
│   └── series_info.txt       # Information about this series
├── [SeriesName2]_[UID]/
│   └── ...
└── ...
```

## Setting Up

1. Install required packages:
```
pip install pydicom numpy pillow
```

2. Update the input and output directories in each script if needed.

## Notes for VLM Analysis

When using the extracted images with a VLM:

1. The PNG files are ready for direct input to most VLMs
2. For better context, you may want to include:
   - The series_info.txt file for information about the MRI sequence
   - The metadata text file associated with each image
3. The HTML report provides a good overview of the available series and can help identify which ones are most relevant for your analysis.

## License

[Your license information here]

## Contact

[Your contact information here]
