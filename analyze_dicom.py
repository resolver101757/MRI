import pydicom
import numpy as np
from pathlib import Path
from PIL import Image

# Path to your DICOM files
dicom_dir = Path(r"D:\personal\scans\mri\Images")

# Get first DICOM file for analysis
sample_file = next(dicom_dir.glob("*.DCM"))
print(f"Analyzing file: {sample_file}")

# Read the DICOM file
ds = pydicom.dcmread(sample_file)

# Print basic metadata
print("\n=== Basic DICOM Metadata ===")
print(f"Patient Name: {ds.PatientName if 'PatientName' in ds else 'Not available'}")
print(f"Patient ID: {ds.PatientID if 'PatientID' in ds else 'Not available'}")
print(f"Modality: {ds.Modality if 'Modality' in ds else 'Not available'}")
print(f"Study Date: {ds.StudyDate if 'StudyDate' in ds else 'Not available'}")
print(f"Series Description: {ds.SeriesDescription if 'SeriesDescription' in ds else 'Not available'}")
print(f"Manufacturer: {ds.Manufacturer if 'Manufacturer' in ds else 'Not available'}")

# Print image details
print("\n=== Image Information ===")

try:
    # Get pixel data
    pixel_data = ds.pixel_array
    
    print(f"Image Shape: {pixel_data.shape}")
    print(f"Data Type: {pixel_data.dtype}")
    print(f"Bits Allocated: {ds.BitsAllocated if 'BitsAllocated' in ds else 'Not available'}")
    print(f"Bits Stored: {ds.BitsStored if 'BitsStored' in ds else 'Not available'}")
    print(f"High Bit: {ds.HighBit if 'HighBit' in ds else 'Not available'}")
    print(f"Pixel Representation: {ds.PixelRepresentation if 'PixelRepresentation' in ds else 'Not available'}")
    print(f"Window Center: {ds.WindowCenter if 'WindowCenter' in ds else 'Not available'}")
    print(f"Window Width: {ds.WindowWidth if 'WindowWidth' in ds else 'Not available'}")
    
    # Normalize pixel data to 0-255 for saving as image
    pixel_data_normalized = ((pixel_data - pixel_data.min()) / 
                            (pixel_data.max() - pixel_data.min()) * 255).astype(np.uint8)
    
    # Save as PNG
    img = Image.fromarray(pixel_data_normalized)
    img.save('dicom_sample.png')
    print("\nSaved sample image to 'dicom_sample.png'")
    
except Exception as e:
    print(f"Error processing pixel data: {e}")

# Display a sample of all attributes
print("\n=== DICOM Header Sample (first 20 elements) ===")
for i, elem in enumerate(ds):
    if i >= 20:  # Limit to first 20 elements to avoid overwhelming output
        break
    print(f"{elem.tag}: {elem.name} = {elem.value}")

# Count series and studies in the directory
print("\n=== Series/Study Information ===")
try:
    # Dictionary to store unique series and studies
    studies = {}
    series = set()
    
    # Process first 10 files for a quick overview
    for i, file_path in enumerate(dicom_dir.glob("*.DCM")):
        if i >= 10:  # Limit to 10 files for performance
            break
        
        ds_temp = pydicom.dcmread(file_path, stop_before_pixels=True)
        study_uid = ds_temp.StudyInstanceUID if 'StudyInstanceUID' in ds_temp else 'Unknown'
        series_uid = ds_temp.SeriesInstanceUID if 'SeriesInstanceUID' in ds_temp else 'Unknown'
        series_desc = ds_temp.SeriesDescription if 'SeriesDescription' in ds_temp else 'Unknown'
        
        if study_uid not in studies:
            studies[study_uid] = set()
        
        studies[study_uid].add((series_uid, series_desc))
        series.add(series_uid)
    
    print(f"Found {len(studies)} unique studies")
    print(f"Found {len(series)} unique series")
    
    # Print series info
    print("\nSeries information:")
    for study_uid, series_set in studies.items():
        print(f"Study UID: {study_uid}")
        for series_uid, series_desc in series_set:
            print(f"  - Series: {series_desc} (UID: {series_uid})")
            
except Exception as e:
    print(f"Error analyzing directory: {e}") 