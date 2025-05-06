import pydicom
import numpy as np
from pathlib import Path
from PIL import Image
import os
import shutil

def process_dicoms(input_dir, output_dir):
    """
    Process DICOM files from input directory and save them as PNG files organized by series
    
    Args:
        input_dir: Path to input directory containing DICOM files
        output_dir: Path to output directory where PNG files will be saved
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create a subdirectory for anonymized files (optional)
    anon_dir = output_path / "anonymized_dicoms"
    anon_dir.mkdir(exist_ok=True)
    
    # Dictionary to organize files by series
    series_dict = {}
    
    # First pass: organize files by series
    print("Organizing files by series...")
    for dcm_file in input_path.glob("*.DCM"):
        try:
            # Read DICOM file (stop before pixel data for faster metadata reading)
            ds = pydicom.dcmread(dcm_file, stop_before_pixels=True)
            
            # Get series UID and description
            series_uid = ds.SeriesInstanceUID if 'SeriesInstanceUID' in ds else 'unknown'
            series_desc = ds.SeriesDescription if 'SeriesDescription' in ds else 'unknown'
            
            # Clean series description for use as directory name
            clean_desc = ''.join(c if c.isalnum() else '_' for c in series_desc)
            series_name = f"{clean_desc}_{series_uid[-8:]}"
            
            # Add to dictionary
            if series_name not in series_dict:
                series_dict[series_name] = []
            
            series_dict[series_name].append(dcm_file)
            
        except Exception as e:
            print(f"Error reading {dcm_file.name}: {e}")
    
    print(f"Found {len(series_dict)} unique series")
    
    # Second pass: convert files to PNG by series
    for series_name, file_list in series_dict.items():
        # Create directory for this series
        series_dir = output_path / series_name
        series_dir.mkdir(exist_ok=True)
        
        print(f"Processing series: {series_name} ({len(file_list)} files)")
        
        # Process files in this series
        for i, dcm_file in enumerate(file_list):
            try:
                # Read DICOM file with pixel data
                ds = pydicom.dcmread(dcm_file)
                
                # Create anonymized copy (if needed)
                if 'PatientName' in ds:
                    ds.PatientName = "ANONYMOUS"
                if 'PatientID' in ds:
                    ds.PatientID = "ID" + str(abs(hash(str(ds.PatientID))) % 10000)
                if 'PatientBirthDate' in ds:
                    ds.PatientBirthDate = ""
                
                # Save anonymized DICOM
                anon_file = anon_dir / dcm_file.name
                ds.save_as(anon_file)
                
                # Get pixel data
                pixel_array = ds.pixel_array
                
                # Apply windowing if available
                if all(attr in ds for attr in ['WindowCenter', 'WindowWidth']):
                    center = ds.WindowCenter
                    width = ds.WindowWidth
                    
                    # Handle multiple window center/width values
                    if isinstance(center, pydicom.multival.MultiValue):
                        center = center[0]
                    if isinstance(width, pydicom.multival.MultiValue):
                        width = width[0]
                        
                    y_min = center - width // 2
                    y_max = center + width // 2
                    
                    # Apply window
                    pixel_array = np.clip(pixel_array, y_min, y_max)
                
                # Normalize pixel array to 0-255
                if pixel_array.max() != pixel_array.min():
                    pixel_array = ((pixel_array - pixel_array.min()) / 
                                  (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
                else:
                    pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)
                
                # Save as PNG
                img = Image.fromarray(pixel_array)
                img_file = series_dir / f"slice_{i:04d}.png"
                img.save(img_file)
                
                # Save image metadata
                with open(series_dir / f"slice_{i:04d}_metadata.txt", 'w') as f:
                    # Write key metadata
                    f.write(f"Filename: {dcm_file.name}\n")
                    f.write(f"Series Description: {ds.SeriesDescription if 'SeriesDescription' in ds else 'N/A'}\n")
                    f.write(f"Image Type: {ds.ImageType if 'ImageType' in ds else 'N/A'}\n")
                    f.write(f"Acquisition Date/Time: {ds.AcquisitionDate if 'AcquisitionDate' in ds else 'N/A'} {ds.AcquisitionTime if 'AcquisitionTime' in ds else 'N/A'}\n")
                    
                    # Add slice location if available
                    if 'SliceLocation' in ds:
                        f.write(f"Slice Location: {ds.SliceLocation}\n")
                    
                    # Add instance number if available
                    if 'InstanceNumber' in ds:
                        f.write(f"Instance Number: {ds.InstanceNumber}\n")
                
                if i % 10 == 0:
                    print(f"  Processed {i+1}/{len(file_list)}")
                    
            except Exception as e:
                print(f"Error processing {dcm_file.name}: {e}")
        
        # Create a summary file for this series
        with open(series_dir / "series_info.txt", 'w') as f:
            try:
                # Use first file for series info
                sample_ds = pydicom.dcmread(file_list[0], stop_before_pixels=True)
                
                f.write(f"Series Description: {sample_ds.SeriesDescription if 'SeriesDescription' in sample_ds else 'N/A'}\n")
                f.write(f"Series UID: {sample_ds.SeriesInstanceUID if 'SeriesInstanceUID' in sample_ds else 'N/A'}\n")
                f.write(f"Study Description: {sample_ds.StudyDescription if 'StudyDescription' in sample_ds else 'N/A'}\n")
                f.write(f"Number of Images: {len(file_list)}\n")
                f.write(f"Modality: {sample_ds.Modality if 'Modality' in sample_ds else 'N/A'}\n")
                f.write(f"Manufacturer: {sample_ds.Manufacturer if 'Manufacturer' in sample_ds else 'N/A'}\n")
                
                if all(attr in sample_ds for attr in ['Rows', 'Columns']):
                    f.write(f"Image Dimensions: {sample_ds.Rows}x{sample_ds.Columns}\n")
                
            except Exception as e:
                f.write(f"Error creating summary: {e}\n")
    
    print("Processing complete!")

if __name__ == "__main__":
    # Path to DICOM files
    input_dir = r"D:\personal\scans\mri\Images"
    
    # Path to output directory
    output_dir = r"D:\personal\scans\mri\extracted_for_vlm"
    
    process_dicoms(input_dir, output_dir) 